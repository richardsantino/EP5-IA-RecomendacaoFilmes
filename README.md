# Recomendação de Filmes
### Programa feito para a matéria de Inteligência Artificial do 5° Semestre de Ciência da Computação

### Por Caroline Viana e Richard Santino

---

## Descrição
O projeto é a construção de um sistema de recomendação de filmes, feito utilizando o [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset).

Para isso, foi utilizado o kNN em um modelo que considera similaridade entre os usuários.

## Conteúdo e execução

O projeto, possui uma série de arquivos, mas todos são necessários para a execução. É preciso baixar todos eles e mantê-los na mesma pasta para o momento da execução.

Os arquivos `movies_metadata.csv`, `ratings_small.csv` e `links_small.csv` são os dados que vieram do dataset, contendo, respectivamente, informações sobre cada um dos filmes (incluindo título, notas, posteres, entre outros), as avaliações dos usuários para cada filme, e os links que conectam os IDs dos filmes em `movies_metadata.csv`aos IDs presentes no arquivo `ratings_small.csv`.

O arquivo `Wuv.csv` foi gerado durante a execução do programa. Nele, estão os resultados do cálculo da similaridade W(u,v) para cada usuário.

Para iniciar o programa, deve-se executar o arquivo `main.py`, tanto por IDE quanto por terminal, mas é importante haver espaço para que as informações possam ser impressas da forma desejada.

Por conta da quantidade de arquivos, e o fato de que a recomendação para cada usuário é feita na hora, a execução do programa pode demorar.
