import pandas as pd
import numpy as np
import csv
import math
import os

# Link do Dataset:
# https://www.kaggle.com/rounakbanik/the-movies-dataset

dataset = pd.read_csv("./ratings_small.csv")

# Função que faz o calculo da similaridade W(u,v)
# É o retorno dela que é salvo no arquivo CSV, que é a similaridade entre 2 usuários, usando a correlação de pearson
def calculateWuv(u, v):
  filt = (dataset['userId'] == u)
  uData = dataset.loc[filt]

  filt = (dataset['userId'] == v)
  vData = dataset.loc[filt]

  smaller = vData if len(uData.index) > len(vData.index) else uData
  bigger = vData if len(uData.index) <= len(vData.index) else uData

  bothLiked = []
  for i in range(0, len(smaller.index) - 1):
    for j in range(0, len(bigger.index) - 1):
      if smaller['movieId'].values[i] == bigger['movieId'].values[j]:
        bothLiked.append(smaller['movieId'].values[i])
        break
  
  if len(bothLiked) == 0:
    # Os usuários não assistiram aos mesmos filmes
    return 0
  else:
    uMean = uData['rating'].mean()
    vMean = vData['rating'].mean()

    fracNum = 0
    fracDenU = 0
    fracDenV = 0

    for i in bothLiked:

      fil = (uData['movieId'] == i)
      uC = uData.loc[fil]
      uRating = uC['rating'].values[0]
      ru_ruMean = uRating - uMean

      fil = (vData['movieId'] == i)
      vC = vData.loc[fil]
      vRating = vC['rating'].values[0]   
      rv_rvMean = vRating - vMean

      fracNum += (ru_ruMean * rv_rvMean)

      fracDenU += pow(ru_ruMean, 2)
      fracDenV += pow(rv_rvMean, 2)
    
    fracDen = math.sqrt(fracDenU) * math.sqrt(fracDenV)
    W = fracNum / fracDen if fracDen != 0 else 0
    return W

# Pega os top N usuarios mais similares com o usuario U
def getTopNSimilarities(u, topN, dt):
  filt = (dt['u']  == u)
  uSim = dt.loc[filt]
  sortedDt = uSim.sort_values(by = 'W(u,v)', ascending = False)
  return sortedDt.head(topN)

# Função pra imprimir loading
def printingProgress(item, totalCount):
  os.system('cls' if os.name == 'nt' else 'clear')
  print("We're processing the items")
  print("Please, wait. This might take a while.")
  print(str(item) + "/" + str(totalCount))

# Avalia todos os itens que o usuário não assistiu, baseado nos outros usuários similares e retorna os ids dos top 10 filmes recomendados
def sortAndRecomendItems(user, topSimilarUsers):
  filt = (dataset['userId'] == user)
  userWatched = dataset.loc[filt]
  dtM = pd.read_csv("./movies_metadata.csv")
  
  # Lista os filmes não assistidos
  unwatchedMovieIdList = []
  for i in range(2, math.floor(len(dtM.index))):
    if i not in userWatched['movieId'].values:
      unwatchedMovieIdList.append(i)

  fracNum = 0
  fracDen = 0
  
  recomendations = {}
  for item in unwatchedMovieIdList:
    printingProgress(item,unwatchedMovieIdList[-1])

    for userId in topSimilarUsers['v'].values:
      filt = (dataset['userId'] == userId)
      userDt = dataset.loc[filt]
      filt2 = (userDt['movieId'] == item)
      rating = userDt.loc[filt2]
      r = rating['rating'].values[0] if len(rating.index) != 0 else 0
      filt3 = (topSimilarUsers['u'] == user) & (topSimilarUsers['v'] == userId)
      wuv = topSimilarUsers.loc[filt3]
      w = wuv['W(u,v)'].values[0]
      
      fracNum += r * w
      fracDen += abs(w)

    recomendations[item] = fracNum / fracDen if fracDen != 0 else 0

  recomm = pd.Series(recomendations, name="recommend")
  recomm.index.name = "item"
  recomm.reset_index()
  recomm.columns = ['item','infer']
  return recomm.sort_values(ascending = False)

# Para novos usuários, recomendar os filmes com pontuação média mais alta, desde que tenha sido votado por pelo menos 5000 usuários
def recomendNewUser():
  movieTitles = []
  moviesDt = pd.read_csv("./movies_metadata.csv")

  filt = (moviesDt['vote_count']  >= 5000)
  mVotes = moviesDt.loc[filt]

  mBest = mVotes.sort_values(by = 'vote_average', ascending = False)

  for i in range(0, 10):
    movieTitles.append(mBest['original_title'].values[i])

  return movieTitles

# Pega os ids dos top 10 filmes recomendados e devolve os respectivos títulos
def getMovieTitles(bestRecomend):
  movieId = []
  extra = 10
  for i in range(0, 10):
    movieId.append(bestRecomend.index[i])

  moviesIds = pd.read_csv("./links_small.csv")
  moviesDt = pd.read_csv("./movies_metadata.csv")

  moviesDt['imdb_id'] = moviesDt['imdb_id'].replace(np.nan, 0)
  
  movieTitles = []
  
  for movie in movieId:
    fil = (moviesIds['movieId'] == movie)
    movieIdsAll = moviesIds.loc[fil]
    if movieIdsAll.empty:
      movieId.append(bestRecomend.index[extra])
      extra += 1
      continue
    imdbId = movieIdsAll['imdbId'].values[0]
    
    imdbIdS = str(imdbId)
    while len(imdbIdS) != 7:
      imdbIdS = "0" + imdbIdS
    imdbIdS = "tt" + imdbIdS
    
    filt = (moviesDt['imdb_id'] == imdbIdS)
    movieData = moviesDt.loc[filt]
    title = movieData['original_title'].values[0]
    movieTitles.append(title)
  
  return movieTitles

# --- Inicialização --- #

# Preencher a tabela de similaridade uma única vez, já que os usuários são estáticos
if os.stat("./Wuv.csv").st_size == 0:
  with open('Wuv.csv', 'w', newline='') as wFile:
    writer = csv.writer(wFile)
    writer.writerow(["u", "v", "W(u,v)"])
    last = dataset.tail(1)
    counter = last['userId'].values[0] + 1

    for i in range(0, counter):
      for j in range(0, counter):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("We're filling up the user similarity table.\nPlease, wait. This might (and will) take a while.")
        print("Take the time waiting to drink some water or to pet your dog/cat :D")
        print("Processing user: " + str(i) + "/" + str(counter - 1))
        print("Pairing processing: " + str(j) + "/" + str(counter - 1))

        if i != j:
          W = calculateWuv(i,j)
          writer.writerow([i, j, W])
    print("Processing complete!\n")


print("Pick a user to make a recommendation.\nYou can choose a value between 1 and 671.\nIf you wish to test on a new user, type 0 (zero).")
choice = int(input("Your choice: "))
user = 2
if choice >= 0 and choice <= 671:
  user = choice
else:
  print("You typed a value out of range\nComputing recommendations for user #2")
  user = 2

dtW = pd.read_csv("./Wuv.csv")
dtW["W(u,v)"] = dtW["W(u,v)"].replace(np.nan, 0)
WuvDataset = getTopNSimilarities(user, 5, dtW)
recomendations = sortAndRecomendItems(user, WuvDataset)
if recomendations.values[0] == 0.0:
  myMovies = recomendNewUser()
else:
  myMovies = getMovieTitles(recomendations.head(20))

os.system('cls' if os.name == 'nt' else 'clear')
print("Processing complete!\n")
print("Recommended for user #" + str(user))
for movie in myMovies:
  print("- " + str(movie))