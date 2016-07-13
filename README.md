# systemt

###stockcode.py 
증권 코드를 sqlite code.db에 구축 합니다.

"
sparrow-mac-mini2:SystemT sparrow$ sqlite3 code.db 
SQLite version 3.8.4.1 2014-03-11 15:27:36
Enter ".help" for usage hints.
sqlite> select * from code limit 10
   ...> ;
0|A000020|동화약품|거래소
1|A000030|우리은행|거래소
2|A000040|KR모터스|거래소
3|A000050|경방|거래소
4|A000060|메리츠화재|거래소
5|A000070|삼양홀딩스|거래소
6|A000075|삼양홀딩스우|거래소
7|A000080|하이트진로|거래소
8|A000087|하이트진로2우B|거래소
9|A000100|유한양행|거래소

sqlite> select sql from sqlite_master where name = 'CODE';
CREATE TABLE "CODE" (
"index" INTEGER,
  "CODE" TEXT,
  "NAME" TEXT,
  "TYPE" TEXT
)
sqlite> 
"

###datacrawler.py
증권 종뫀 코드에 있는 주식 종목들의
시가 고가 저가 종가 거래량을 일자 별로 각각의 코드명의 테이블로 price.db에 저장 합니다.

"
sparrow-mac-mini2:SystemT sparrow$ sqlite3 price.db 
SQLite version 3.8.4.1 2014-03-11 15:27:36
Enter ".help" for usage hints.
sqlite> select * from A000020 limit 10;
0|10450|2016-07-13 00:00:00|10850|10400|10750|226212
1|10550|2016-07-12 00:00:00|10750|10350|10650|213586
2|10650|2016-07-11 00:00:00|10850|10550|10750|245693
3|10600|2016-07-08 00:00:00|11050|10500|11000|409317
4|10850|2016-07-07 00:00:00|11100|10200|10300|1346083
5|10100|2016-07-06 00:00:00|10400|9990|10250|198457
6|10350|2016-07-05 00:00:00|10450|10200|10400|156010
7|10400|2016-07-04 00:00:00|10400|9900|10000|275210
8|9960|2016-07-01 00:00:00|10200|9960|10200|208228
9|10100|2016-06-30 00:00:00|10400|9760|9850|466248
sqlite> 

sqlite> select sql from sqlite_master where name = 'A000020';
CREATE TABLE "A000020" (
"index" INTEGER,
  "CLOSE" INTEGER,
  "DATE" TIMESTAMP,
  "HIGH" INTEGER,
  "LOW" INTEGER,
  "OPEN" INTEGER,
  "VOLUME" INTEGER
)

"
