from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selectolax.lexbor import LexborHTMLParser
import os, json
from typing import List, Dict, Callable
import time, random, re
import pandas as pd
import requests
import io
from io import BytesIO
from io import StringIO
from bs4 import BeautifulSoup
import glob as glob
from fuzzywuzzy import fuzz
import numpy as np
from pymed import PubMed
import chardet
import urllib.request
from nltk.corpus import stopwords
import unicodedata
from unidecode import unidecode
from Bio import Entrez
import requests
import re
import PyPDF2
import urllib.request
Entrez.email = [ENTER EMAIL] # Replace with your email
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'email': [ENTER EMAIL]  # Replace with your email
}
