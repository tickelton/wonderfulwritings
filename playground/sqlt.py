#!/usr/bin/env python

import sqlite3

conn = sqlite3.connect('/media/ramdisk/example.db')

c = conn.cursor()

c.execute('''
  CREATE  TABLE "main"."twot_data" (
      "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
      "title" TEXT NOT NULL ,
      "author" TEXT NOT NULL ,
      "rating" FLOAT NOT NULL  DEFAULT 0.0,
      "count_1" INTEGER NOT NULL  DEFAULT 0,
      "count_2" INTEGER NOT NULL  DEFAULT 0,
      "count_3" INTEGER NOT NULL  DEFAULT 0,
      "count_4" INTEGER NOT NULL  DEFAULT 0,
      "count_5" INTEGER NOT NULL  DEFAULT 0,
      "count_all" INTEGER NOT NULL  DEFAULT 0,
      "summary" TEXT NOT NULL  DEFAULT "-",
      "url_gtb" TEXT NOT NULL  DEFAULT "-",
      "url_wkp" TEXT NOT NULL  DEFAULT "-",
      "url_azn" TEXT NOT NULL  DEFAULT "-",
      "asin" TEXT NOT NULL  DEFAULT "-")
''')

conn.commit()

conn.close()