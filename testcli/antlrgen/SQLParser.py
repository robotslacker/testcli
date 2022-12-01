# Generated from SQLParser.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,138,456,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,
        20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,
        26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,
        33,7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,
        39,2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,45,2,
        46,7,46,2,47,7,47,2,48,7,48,2,49,7,49,1,0,1,0,1,0,1,1,1,1,1,1,1,
        1,1,1,1,1,3,1,110,8,1,1,2,1,2,3,2,114,8,2,1,3,1,3,1,3,1,3,1,4,1,
        4,1,4,3,4,123,8,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,132,8,4,1,4,1,
        4,1,4,3,4,137,8,4,1,4,1,4,1,4,3,4,142,8,4,1,4,1,4,3,4,146,8,4,1,
        5,1,5,1,5,3,5,151,8,5,1,6,1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,10,1,10,
        1,11,1,11,1,12,1,12,1,13,1,13,1,13,3,13,170,8,13,1,14,1,14,1,15,
        1,15,1,16,1,16,1,17,1,17,1,17,1,17,1,18,1,18,1,18,4,18,185,8,18,
        11,18,12,18,186,3,18,189,8,18,1,19,1,19,1,19,5,19,194,8,19,10,19,
        12,19,197,9,19,1,19,3,19,200,8,19,1,20,1,20,1,20,3,20,205,8,20,1,
        20,3,20,208,8,20,1,21,4,21,211,8,21,11,21,12,21,212,1,22,1,22,1,
        22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,3,22,226,8,22,1,23,1,
        23,1,23,3,23,231,8,23,1,24,1,24,1,24,3,24,236,8,24,1,25,1,25,1,25,
        3,25,241,8,25,1,26,1,26,1,26,3,26,246,8,26,1,27,1,27,1,27,3,27,251,
        8,27,1,28,1,28,1,28,3,28,256,8,28,1,29,1,29,1,29,3,29,261,8,29,1,
        30,1,30,3,30,265,8,30,1,30,3,30,268,8,30,1,31,1,31,1,31,3,31,273,
        8,31,1,32,1,32,1,32,3,32,278,8,32,1,33,1,33,1,33,1,33,1,33,1,33,
        1,33,1,33,1,33,1,33,1,33,1,33,1,33,1,33,1,33,1,33,3,33,296,8,33,
        1,34,1,34,3,34,300,8,34,1,34,3,34,303,8,34,1,34,3,34,306,8,34,1,
        35,1,35,3,35,310,8,35,1,35,3,35,313,8,35,1,35,3,35,316,8,35,1,36,
        1,36,1,36,3,36,321,8,36,1,36,3,36,324,8,36,1,37,1,37,1,37,3,37,329,
        8,37,1,37,3,37,332,8,37,1,38,1,38,1,38,1,38,5,38,338,8,38,10,38,
        12,38,341,9,38,1,38,3,38,344,8,38,1,38,3,38,347,8,38,1,38,3,38,350,
        8,38,1,38,3,38,353,8,38,1,39,1,39,1,39,4,39,358,8,39,11,39,12,39,
        359,1,39,3,39,363,8,39,1,39,3,39,366,8,39,1,40,1,40,1,40,3,40,371,
        8,40,1,40,3,40,374,8,40,1,41,1,41,1,41,1,42,1,42,1,42,1,42,1,42,
        1,42,1,42,3,42,386,8,42,1,42,3,42,389,8,42,1,42,3,42,392,8,42,1,
        43,1,43,1,43,3,43,397,8,43,1,43,3,43,400,8,43,1,44,1,44,3,44,404,
        8,44,1,44,3,44,407,8,44,1,45,1,45,1,45,1,45,1,45,3,45,414,8,45,1,
        45,3,45,417,8,45,1,45,3,45,420,8,45,1,46,1,46,1,46,3,46,425,8,46,
        1,46,3,46,428,8,46,1,47,1,47,1,47,3,47,433,8,47,1,48,1,48,1,48,3,
        48,438,8,48,1,49,1,49,3,49,442,8,49,1,49,5,49,445,8,49,10,49,12,
        49,448,9,49,1,49,3,49,451,8,49,1,49,3,49,454,8,49,1,49,0,0,50,0,
        2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,
        48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90,
        92,94,96,98,0,8,1,0,53,54,2,0,62,62,64,64,1,0,71,75,3,0,20,20,22,
        30,50,50,1,0,14,15,1,0,11,12,1,0,134,135,1,1,17,17,502,0,100,1,0,
        0,0,2,109,1,0,0,0,4,113,1,0,0,0,6,115,1,0,0,0,8,119,1,0,0,0,10,147,
        1,0,0,0,12,152,1,0,0,0,14,154,1,0,0,0,16,156,1,0,0,0,18,158,1,0,
        0,0,20,160,1,0,0,0,22,162,1,0,0,0,24,164,1,0,0,0,26,166,1,0,0,0,
        28,171,1,0,0,0,30,173,1,0,0,0,32,175,1,0,0,0,34,177,1,0,0,0,36,181,
        1,0,0,0,38,190,1,0,0,0,40,201,1,0,0,0,42,210,1,0,0,0,44,225,1,0,
        0,0,46,227,1,0,0,0,48,232,1,0,0,0,50,237,1,0,0,0,52,242,1,0,0,0,
        54,247,1,0,0,0,56,252,1,0,0,0,58,257,1,0,0,0,60,262,1,0,0,0,62,269,
        1,0,0,0,64,274,1,0,0,0,66,295,1,0,0,0,68,297,1,0,0,0,70,307,1,0,
        0,0,72,317,1,0,0,0,74,325,1,0,0,0,76,333,1,0,0,0,78,354,1,0,0,0,
        80,367,1,0,0,0,82,375,1,0,0,0,84,378,1,0,0,0,86,393,1,0,0,0,88,401,
        1,0,0,0,90,408,1,0,0,0,92,421,1,0,0,0,94,429,1,0,0,0,96,434,1,0,
        0,0,98,439,1,0,0,0,100,101,3,2,1,0,101,102,5,0,0,1,102,1,1,0,0,0,
        103,110,3,66,33,0,104,110,3,38,19,0,105,110,3,40,20,0,106,110,3,
        4,2,0,107,110,3,44,22,0,108,110,5,0,0,1,109,103,1,0,0,0,109,104,
        1,0,0,0,109,105,1,0,0,0,109,106,1,0,0,0,109,107,1,0,0,0,109,108,
        1,0,0,0,110,3,1,0,0,0,111,114,3,8,4,0,112,114,3,6,3,0,113,111,1,
        0,0,0,113,112,1,0,0,0,114,5,1,0,0,0,115,116,5,1,0,0,116,117,5,53,
        0,0,117,118,3,28,14,0,118,7,1,0,0,0,119,120,5,1,0,0,120,122,3,10,
        5,0,121,123,5,52,0,0,122,121,1,0,0,0,122,123,1,0,0,0,123,141,1,0,
        0,0,124,125,3,12,6,0,125,126,5,54,0,0,126,127,3,14,7,0,127,131,5,
        54,0,0,128,129,3,16,8,0,129,130,5,54,0,0,130,132,1,0,0,0,131,128,
        1,0,0,0,131,132,1,0,0,0,132,133,1,0,0,0,133,134,5,58,0,0,134,136,
        3,18,9,0,135,137,3,24,12,0,136,135,1,0,0,0,136,137,1,0,0,0,137,138,
        1,0,0,0,138,139,7,0,0,0,139,140,3,26,13,0,140,142,1,0,0,0,141,124,
        1,0,0,0,141,142,1,0,0,0,142,145,1,0,0,0,143,144,5,55,0,0,144,146,
        3,36,18,0,145,143,1,0,0,0,145,146,1,0,0,0,146,9,1,0,0,0,147,150,
        3,20,10,0,148,149,5,53,0,0,149,151,3,22,11,0,150,148,1,0,0,0,150,
        151,1,0,0,0,151,11,1,0,0,0,152,153,5,61,0,0,153,13,1,0,0,0,154,155,
        5,64,0,0,155,15,1,0,0,0,156,157,5,64,0,0,157,17,1,0,0,0,158,159,
        7,1,0,0,159,19,1,0,0,0,160,161,5,64,0,0,161,21,1,0,0,0,162,163,5,
        64,0,0,163,23,1,0,0,0,164,165,5,63,0,0,165,25,1,0,0,0,166,169,5,
        64,0,0,167,168,5,54,0,0,168,170,5,64,0,0,169,167,1,0,0,0,169,170,
        1,0,0,0,170,27,1,0,0,0,171,172,5,64,0,0,172,29,1,0,0,0,173,174,5,
        64,0,0,174,31,1,0,0,0,175,176,5,64,0,0,176,33,1,0,0,0,177,178,3,
        30,15,0,178,179,5,59,0,0,179,180,3,32,16,0,180,35,1,0,0,0,181,188,
        3,34,17,0,182,183,5,60,0,0,183,185,3,34,17,0,184,182,1,0,0,0,185,
        186,1,0,0,0,186,184,1,0,0,0,186,187,1,0,0,0,187,189,1,0,0,0,188,
        184,1,0,0,0,188,189,1,0,0,0,189,37,1,0,0,0,190,195,5,3,0,0,191,194,
        3,42,21,0,192,194,5,48,0,0,193,191,1,0,0,0,193,192,1,0,0,0,194,197,
        1,0,0,0,195,193,1,0,0,0,195,196,1,0,0,0,196,199,1,0,0,0,197,195,
        1,0,0,0,198,200,5,17,0,0,199,198,1,0,0,0,199,200,1,0,0,0,200,39,
        1,0,0,0,201,202,5,2,0,0,202,204,7,2,0,0,203,205,5,76,0,0,204,203,
        1,0,0,0,204,205,1,0,0,0,205,207,1,0,0,0,206,208,5,77,0,0,207,206,
        1,0,0,0,207,208,1,0,0,0,208,41,1,0,0,0,209,211,7,3,0,0,210,209,1,
        0,0,0,211,212,1,0,0,0,212,210,1,0,0,0,212,213,1,0,0,0,213,43,1,0,
        0,0,214,226,3,46,23,0,215,226,3,48,24,0,216,226,3,50,25,0,217,226,
        3,52,26,0,218,226,3,54,27,0,219,226,3,56,28,0,220,226,3,62,31,0,
        221,226,3,58,29,0,222,226,3,60,30,0,223,226,3,64,32,0,224,226,5,
        17,0,0,225,214,1,0,0,0,225,215,1,0,0,0,225,216,1,0,0,0,225,217,1,
        0,0,0,225,218,1,0,0,0,225,219,1,0,0,0,225,220,1,0,0,0,225,221,1,
        0,0,0,225,222,1,0,0,0,225,223,1,0,0,0,225,224,1,0,0,0,226,45,1,0,
        0,0,227,228,5,5,0,0,228,230,5,80,0,0,229,231,5,17,0,0,230,229,1,
        0,0,0,230,231,1,0,0,0,231,47,1,0,0,0,232,233,5,10,0,0,233,235,5,
        80,0,0,234,236,5,17,0,0,235,234,1,0,0,0,235,236,1,0,0,0,236,49,1,
        0,0,0,237,238,5,6,0,0,238,240,5,80,0,0,239,241,5,17,0,0,240,239,
        1,0,0,0,240,241,1,0,0,0,241,51,1,0,0,0,242,243,5,7,0,0,243,245,5,
        80,0,0,244,246,5,17,0,0,245,244,1,0,0,0,245,246,1,0,0,0,246,53,1,
        0,0,0,247,248,5,9,0,0,248,250,5,80,0,0,249,251,5,17,0,0,250,249,
        1,0,0,0,250,251,1,0,0,0,251,55,1,0,0,0,252,253,5,8,0,0,253,255,5,
        80,0,0,254,256,5,17,0,0,255,254,1,0,0,0,255,256,1,0,0,0,256,57,1,
        0,0,0,257,258,5,13,0,0,258,260,5,80,0,0,259,261,5,17,0,0,260,259,
        1,0,0,0,260,261,1,0,0,0,261,59,1,0,0,0,262,264,7,4,0,0,263,265,5,
        80,0,0,264,263,1,0,0,0,264,265,1,0,0,0,265,267,1,0,0,0,266,268,5,
        17,0,0,267,266,1,0,0,0,267,268,1,0,0,0,268,61,1,0,0,0,269,270,7,
        5,0,0,270,272,5,85,0,0,271,273,5,17,0,0,272,271,1,0,0,0,272,273,
        1,0,0,0,273,63,1,0,0,0,274,275,5,16,0,0,275,277,5,85,0,0,276,278,
        5,17,0,0,277,276,1,0,0,0,277,278,1,0,0,0,278,65,1,0,0,0,279,296,
        3,80,40,0,280,296,3,78,39,0,281,296,3,82,41,0,282,296,3,76,38,0,
        283,296,3,84,42,0,284,296,3,86,43,0,285,296,3,88,44,0,286,296,3,
        90,45,0,287,296,3,98,49,0,288,296,3,72,36,0,289,296,3,68,34,0,290,
        296,3,70,35,0,291,296,3,74,37,0,292,296,3,92,46,0,293,296,3,96,48,
        0,294,296,3,94,47,0,295,279,1,0,0,0,295,280,1,0,0,0,295,281,1,0,
        0,0,295,282,1,0,0,0,295,283,1,0,0,0,295,284,1,0,0,0,295,285,1,0,
        0,0,295,286,1,0,0,0,295,287,1,0,0,0,295,288,1,0,0,0,295,289,1,0,
        0,0,295,290,1,0,0,0,295,291,1,0,0,0,295,292,1,0,0,0,295,293,1,0,
        0,0,295,294,1,0,0,0,296,67,1,0,0,0,297,299,5,32,0,0,298,300,5,48,
        0,0,299,298,1,0,0,0,299,300,1,0,0,0,300,302,1,0,0,0,301,303,5,19,
        0,0,302,301,1,0,0,0,302,303,1,0,0,0,303,305,1,0,0,0,304,306,5,17,
        0,0,305,304,1,0,0,0,305,306,1,0,0,0,306,69,1,0,0,0,307,309,5,33,
        0,0,308,310,5,48,0,0,309,308,1,0,0,0,309,310,1,0,0,0,310,312,1,0,
        0,0,311,313,5,19,0,0,312,311,1,0,0,0,312,313,1,0,0,0,313,315,1,0,
        0,0,314,316,5,17,0,0,315,314,1,0,0,0,315,316,1,0,0,0,316,71,1,0,
        0,0,317,318,5,36,0,0,318,320,7,6,0,0,319,321,5,137,0,0,320,319,1,
        0,0,0,320,321,1,0,0,0,321,323,1,0,0,0,322,324,5,17,0,0,323,322,1,
        0,0,0,323,324,1,0,0,0,324,73,1,0,0,0,325,326,5,35,0,0,326,328,5,
        48,0,0,327,329,5,19,0,0,328,327,1,0,0,0,328,329,1,0,0,0,329,331,
        1,0,0,0,330,332,5,17,0,0,331,330,1,0,0,0,331,332,1,0,0,0,332,75,
        1,0,0,0,333,334,5,40,0,0,334,339,5,102,0,0,335,336,5,101,0,0,336,
        338,5,102,0,0,337,335,1,0,0,0,338,341,1,0,0,0,339,337,1,0,0,0,339,
        340,1,0,0,0,340,343,1,0,0,0,341,339,1,0,0,0,342,344,5,99,0,0,343,
        342,1,0,0,0,343,344,1,0,0,0,344,346,1,0,0,0,345,347,5,100,0,0,346,
        345,1,0,0,0,346,347,1,0,0,0,347,349,1,0,0,0,348,350,5,19,0,0,349,
        348,1,0,0,0,349,350,1,0,0,0,350,352,1,0,0,0,351,353,5,17,0,0,352,
        351,1,0,0,0,352,353,1,0,0,0,353,77,1,0,0,0,354,355,5,41,0,0,355,
        357,5,95,0,0,356,358,5,96,0,0,357,356,1,0,0,0,358,359,1,0,0,0,359,
        357,1,0,0,0,359,360,1,0,0,0,360,362,1,0,0,0,361,363,5,19,0,0,362,
        361,1,0,0,0,362,363,1,0,0,0,363,365,1,0,0,0,364,366,5,17,0,0,365,
        364,1,0,0,0,365,366,1,0,0,0,366,79,1,0,0,0,367,368,5,39,0,0,368,
        370,5,93,0,0,369,371,5,19,0,0,370,369,1,0,0,0,370,371,1,0,0,0,371,
        373,1,0,0,0,372,374,5,17,0,0,373,372,1,0,0,0,373,374,1,0,0,0,374,
        81,1,0,0,0,375,376,5,42,0,0,376,377,5,106,0,0,377,83,1,0,0,0,378,
        385,5,46,0,0,379,386,5,117,0,0,380,386,5,118,0,0,381,386,5,119,0,
        0,382,383,5,113,0,0,383,384,5,114,0,0,384,386,5,120,0,0,385,379,
        1,0,0,0,385,380,1,0,0,0,385,381,1,0,0,0,385,382,1,0,0,0,386,388,
        1,0,0,0,387,389,5,111,0,0,388,387,1,0,0,0,388,389,1,0,0,0,389,391,
        1,0,0,0,390,392,5,17,0,0,391,390,1,0,0,0,391,392,1,0,0,0,392,85,
        1,0,0,0,393,394,5,43,0,0,394,396,5,110,0,0,395,397,5,19,0,0,396,
        395,1,0,0,0,396,397,1,0,0,0,397,399,1,0,0,0,398,400,5,17,0,0,399,
        398,1,0,0,0,399,400,1,0,0,0,400,87,1,0,0,0,401,403,5,44,0,0,402,
        404,5,19,0,0,403,402,1,0,0,0,403,404,1,0,0,0,404,406,1,0,0,0,405,
        407,5,17,0,0,406,405,1,0,0,0,406,407,1,0,0,0,407,89,1,0,0,0,408,
        409,5,47,0,0,409,413,5,124,0,0,410,414,5,126,0,0,411,412,5,127,0,
        0,412,414,5,123,0,0,413,410,1,0,0,0,413,411,1,0,0,0,414,416,1,0,
        0,0,415,417,5,125,0,0,416,415,1,0,0,0,416,417,1,0,0,0,417,419,1,
        0,0,0,418,420,5,17,0,0,419,418,1,0,0,0,419,420,1,0,0,0,420,91,1,
        0,0,0,421,422,5,34,0,0,422,424,5,50,0,0,423,425,5,19,0,0,424,423,
        1,0,0,0,424,425,1,0,0,0,425,427,1,0,0,0,426,428,5,17,0,0,427,426,
        1,0,0,0,427,428,1,0,0,0,428,93,1,0,0,0,429,430,5,37,0,0,430,432,
        5,89,0,0,431,433,7,7,0,0,432,431,1,0,0,0,432,433,1,0,0,0,433,95,
        1,0,0,0,434,435,5,38,0,0,435,437,5,88,0,0,436,438,5,17,0,0,437,436,
        1,0,0,0,437,438,1,0,0,0,438,97,1,0,0,0,439,441,5,45,0,0,440,442,
        5,132,0,0,441,440,1,0,0,0,441,442,1,0,0,0,442,446,1,0,0,0,443,445,
        5,130,0,0,444,443,1,0,0,0,445,448,1,0,0,0,446,444,1,0,0,0,446,447,
        1,0,0,0,447,450,1,0,0,0,448,446,1,0,0,0,449,451,5,131,0,0,450,449,
        1,0,0,0,450,451,1,0,0,0,451,453,1,0,0,0,452,454,5,17,0,0,453,452,
        1,0,0,0,453,454,1,0,0,0,454,99,1,0,0,0,68,109,113,122,131,136,141,
        145,150,169,186,188,193,195,199,204,207,212,225,230,235,240,245,
        250,255,260,264,267,272,277,295,299,302,305,309,312,315,320,323,
        328,331,339,343,346,349,352,359,362,365,370,373,385,388,391,396,
        399,403,406,413,416,419,424,427,432,437,441,446,450,453
    ]

class SQLParser ( Parser ):

    grammarFileName = "SQLParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'_CONNECT'", "'_SESSION'", "'_DISCONNECT'", 
                     "<INVALID>", "'CREATE'", "'INSERT'", "'UPDATE'", "'SELECT'", 
                     "'DELETE'", "'REPLACE'", "'DECLARE'", "<INVALID>", 
                     "'DROP'", "'COMMIT'", "'ROLLBACK'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'.'", "<INVALID>", "'('", "')'", "<INVALID>", "<INVALID>", 
                     "'\"'", "'''", "'\\'", "<INVALID>", "'_EXIT'", "'_QUIT'", 
                     "'_SPOOL'", "'_SLEEP'", "'_USE'", "<INVALID>", "'> {%'", 
                     "'_ASSERT'", "'_START'", "'_LOAD'", "'_HOST'", "'_IF'", 
                     "'_ENDIF'", "'_SET'", "'_LOOP'", "'_WHENEVER'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'?'", "'#'", "'|'", "'//'", 
                     "'='", "'&'", "'JDBC'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'HINT'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'SAVE'", "'RELEASE'", "'RESTORE'", "'SAVEURL'", 
                     "'SHOW'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'LOOP'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'\"\"\"'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'UNTIL'", "<INVALID>", "<INVALID>", "'BREAK'", 
                     "'END'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'ERROR'", "<INVALID>", "<INVALID>", "'EXIT'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'API'", "'SQL'" ]

    symbolicNames = [ "<INVALID>", "CONNECT", "SESSION", "DISCONNECT", "MINUS_MINUS_COMMENT", 
                      "SQL_CREATE", "SQL_INSERT", "SQL_UPDATE", "SQL_SELECT", 
                      "SQL_DELETE", "SQL_REPLACE", "SQL_DECLARE", "SQL_BEGIN", 
                      "SQL_DROP", "SQL_COMMIT", "SQL_ROLLBACK", "SQL_CREATE_PROCEDURE", 
                      "CRLF", "COMMA", "SEMICOLON", "COLON", "AT", "DOT", 
                      "SLASH", "BRACKET_OPEN", "BRACKET_CLOSE", "SQUARE_OPEN", 
                      "SQUARE_CLOSE", "DOUBLE_QUOTE", "SINGLE_QUOTE", "ESCAPE", 
                      "SPACE", "EXIT", "QUIT", "SPOOL", "SLEEP", "USE", 
                      "ECHO_OPEN", "SCRIPT_OPEN", "ASSERT", "START", "LOAD", 
                      "HOST", "IF", "ENDIF", "SET", "LOOP", "WHENEVER", 
                      "INT", "DECIMAL", "String", "CONNECT_SPACE", "CONNECT_AT", 
                      "CONNECT_SLASH", "CONNECT_COLON", "CONNECT_QUESTION", 
                      "CONNECT_POUND", "CONNECT_OR", "CONNECT_DASH", "CONNECT_EQUAL", 
                      "CONNECT_PARA_AND", "JDBC", "IPV4", "CONNECT_PORT", 
                      "CONNECT_STRING", "CommentString", "HINT_SP", "HINT", 
                      "HINT_CLOSE", "HINT_STRING", "SESSION_SPACE", "SESSION_SAVE", 
                      "SESSION_RELEASE", "SESSION_RESTORE", "SESSION_SAVEURL", 
                      "SESSION_SHOW", "SESSION_NAME", "SESSION_END", "SQL_CRLF", 
                      "SQL_SPACE", "SQL_END", "SQL_STRING", "SQL_SINGLE", 
                      "SQL_OTHER", "SQL_PROCEDURE_CRLF", "SQL_SLASH", "SQL_PROCEDURE_SLASH", 
                      "SQLProcedureStatement", "ScriptBlock", "EchoBlock", 
                      "ASSERT_SPACE", "ASSERT_OPEN", "ASSERT_CLOSE", "ASSERT_EXPRESSION", 
                      "LOAD_SPACE", "LOAD_OPTION", "LOAD_EXPRESSION", "LOAD_CRLF", 
                      "START_SPACE", "START_LOOP", "START_INT", "START_COMMA", 
                      "START_EXPRESSION", "START_CRLF", "HOST_SPACE", "HOST_TAG", 
                      "HOST_BLOCK", "IF_SPACE", "IF_OPEN", "IF_CLOSE", "IF_EXPRESSION", 
                      "LOOP_SEMICOLON", "LOOP_SPACE", "LOOP_BEGIN", "LOOP_UNTIL", 
                      "LOOP_OPEN", "LOOP_CLOSE", "LOOP_BREAK", "LOOP_END", 
                      "LOOP_CONTINUE", "LOOP_EXPRESSION", "LOOP_CRLF", "WHENEVER_SPACE", 
                      "WHENEVER_EXITCODE", "WHENEVER_ERROR", "WHENEVER_SEMICOLON", 
                      "WHENEVER_CONTINUE", "WHENEVER_EXIT", "WHENEVER_CRLF", 
                      "SET_SPACE", "SET_EXPRESSION", "SET_SEMICOLON", "SET_AT", 
                      "SET_CRLF", "USE_API", "USE_SQL", "USE_SPACE", "USE_SEMICOLON", 
                      "USE_CRLF" ]

    RULE_prog = 0
    RULE_command = 1
    RULE_connect = 2
    RULE_connectlocal = 3
    RULE_connectjdbc = 4
    RULE_connectUserInfo = 5
    RULE_connectDriver = 6
    RULE_connectDriverSchema = 7
    RULE_connectDriverType = 8
    RULE_connectHost = 9
    RULE_connectUser = 10
    RULE_connectPassword = 11
    RULE_connectPort = 12
    RULE_connectService = 13
    RULE_connectlocalService = 14
    RULE_connectParameterName = 15
    RULE_connectParameterValue = 16
    RULE_connectParameter = 17
    RULE_connectParameters = 18
    RULE_disconnect = 19
    RULE_session = 20
    RULE_expression = 21
    RULE_sql = 22
    RULE_sqlCreate = 23
    RULE_sqlReplace = 24
    RULE_sqlInsert = 25
    RULE_sqlUpdate = 26
    RULE_sqlDelete = 27
    RULE_sqlSelect = 28
    RULE_sqlDrop = 29
    RULE_sqlCommitRollback = 30
    RULE_sqlDeclare = 31
    RULE_sqlCreateProcedure = 32
    RULE_baseCommand = 33
    RULE_exit = 34
    RULE_quit = 35
    RULE_use = 36
    RULE_sleep = 37
    RULE_start = 38
    RULE_load = 39
    RULE_assert = 40
    RULE_host = 41
    RULE_loop = 42
    RULE_if = 43
    RULE_endif = 44
    RULE_whenever = 45
    RULE_spool = 46
    RULE_echo = 47
    RULE_script = 48
    RULE_set = 49

    ruleNames =  [ "prog", "command", "connect", "connectlocal", "connectjdbc", 
                   "connectUserInfo", "connectDriver", "connectDriverSchema", 
                   "connectDriverType", "connectHost", "connectUser", "connectPassword", 
                   "connectPort", "connectService", "connectlocalService", 
                   "connectParameterName", "connectParameterValue", "connectParameter", 
                   "connectParameters", "disconnect", "session", "expression", 
                   "sql", "sqlCreate", "sqlReplace", "sqlInsert", "sqlUpdate", 
                   "sqlDelete", "sqlSelect", "sqlDrop", "sqlCommitRollback", 
                   "sqlDeclare", "sqlCreateProcedure", "baseCommand", "exit", 
                   "quit", "use", "sleep", "start", "load", "assert", "host", 
                   "loop", "if", "endif", "whenever", "spool", "echo", "script", 
                   "set" ]

    EOF = Token.EOF
    CONNECT=1
    SESSION=2
    DISCONNECT=3
    MINUS_MINUS_COMMENT=4
    SQL_CREATE=5
    SQL_INSERT=6
    SQL_UPDATE=7
    SQL_SELECT=8
    SQL_DELETE=9
    SQL_REPLACE=10
    SQL_DECLARE=11
    SQL_BEGIN=12
    SQL_DROP=13
    SQL_COMMIT=14
    SQL_ROLLBACK=15
    SQL_CREATE_PROCEDURE=16
    CRLF=17
    COMMA=18
    SEMICOLON=19
    COLON=20
    AT=21
    DOT=22
    SLASH=23
    BRACKET_OPEN=24
    BRACKET_CLOSE=25
    SQUARE_OPEN=26
    SQUARE_CLOSE=27
    DOUBLE_QUOTE=28
    SINGLE_QUOTE=29
    ESCAPE=30
    SPACE=31
    EXIT=32
    QUIT=33
    SPOOL=34
    SLEEP=35
    USE=36
    ECHO_OPEN=37
    SCRIPT_OPEN=38
    ASSERT=39
    START=40
    LOAD=41
    HOST=42
    IF=43
    ENDIF=44
    SET=45
    LOOP=46
    WHENEVER=47
    INT=48
    DECIMAL=49
    String=50
    CONNECT_SPACE=51
    CONNECT_AT=52
    CONNECT_SLASH=53
    CONNECT_COLON=54
    CONNECT_QUESTION=55
    CONNECT_POUND=56
    CONNECT_OR=57
    CONNECT_DASH=58
    CONNECT_EQUAL=59
    CONNECT_PARA_AND=60
    JDBC=61
    IPV4=62
    CONNECT_PORT=63
    CONNECT_STRING=64
    CommentString=65
    HINT_SP=66
    HINT=67
    HINT_CLOSE=68
    HINT_STRING=69
    SESSION_SPACE=70
    SESSION_SAVE=71
    SESSION_RELEASE=72
    SESSION_RESTORE=73
    SESSION_SAVEURL=74
    SESSION_SHOW=75
    SESSION_NAME=76
    SESSION_END=77
    SQL_CRLF=78
    SQL_SPACE=79
    SQL_END=80
    SQL_STRING=81
    SQL_SINGLE=82
    SQL_OTHER=83
    SQL_PROCEDURE_CRLF=84
    SQL_SLASH=85
    SQL_PROCEDURE_SLASH=86
    SQLProcedureStatement=87
    ScriptBlock=88
    EchoBlock=89
    ASSERT_SPACE=90
    ASSERT_OPEN=91
    ASSERT_CLOSE=92
    ASSERT_EXPRESSION=93
    LOAD_SPACE=94
    LOAD_OPTION=95
    LOAD_EXPRESSION=96
    LOAD_CRLF=97
    START_SPACE=98
    START_LOOP=99
    START_INT=100
    START_COMMA=101
    START_EXPRESSION=102
    START_CRLF=103
    HOST_SPACE=104
    HOST_TAG=105
    HOST_BLOCK=106
    IF_SPACE=107
    IF_OPEN=108
    IF_CLOSE=109
    IF_EXPRESSION=110
    LOOP_SEMICOLON=111
    LOOP_SPACE=112
    LOOP_BEGIN=113
    LOOP_UNTIL=114
    LOOP_OPEN=115
    LOOP_CLOSE=116
    LOOP_BREAK=117
    LOOP_END=118
    LOOP_CONTINUE=119
    LOOP_EXPRESSION=120
    LOOP_CRLF=121
    WHENEVER_SPACE=122
    WHENEVER_EXITCODE=123
    WHENEVER_ERROR=124
    WHENEVER_SEMICOLON=125
    WHENEVER_CONTINUE=126
    WHENEVER_EXIT=127
    WHENEVER_CRLF=128
    SET_SPACE=129
    SET_EXPRESSION=130
    SET_SEMICOLON=131
    SET_AT=132
    SET_CRLF=133
    USE_API=134
    USE_SQL=135
    USE_SPACE=136
    USE_SEMICOLON=137
    USE_CRLF=138

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def command(self):
            return self.getTypedRuleContext(SQLParser.CommandContext,0)


        def EOF(self):
            return self.getToken(SQLParser.EOF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_prog

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProg" ):
                return visitor.visitProg(self)
            else:
                return visitor.visitChildren(self)




    def prog(self):

        localctx = SQLParser.ProgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_prog)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 100
            self.command()
            self.state = 101
            self.match(SQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def baseCommand(self):
            return self.getTypedRuleContext(SQLParser.BaseCommandContext,0)


        def disconnect(self):
            return self.getTypedRuleContext(SQLParser.DisconnectContext,0)


        def session(self):
            return self.getTypedRuleContext(SQLParser.SessionContext,0)


        def connect(self):
            return self.getTypedRuleContext(SQLParser.ConnectContext,0)


        def sql(self):
            return self.getTypedRuleContext(SQLParser.SqlContext,0)


        def EOF(self):
            return self.getToken(SQLParser.EOF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_command

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand" ):
                return visitor.visitCommand(self)
            else:
                return visitor.visitChildren(self)




    def command(self):

        localctx = SQLParser.CommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_command)
        try:
            self.state = 109
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
                self.enterOuterAlt(localctx, 1)
                self.state = 103
                self.baseCommand()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 104
                self.disconnect()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 3)
                self.state = 105
                self.session()
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 4)
                self.state = 106
                self.connect()
                pass
            elif token in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]:
                self.enterOuterAlt(localctx, 5)
                self.state = 107
                self.sql()
                pass
            elif token in [-1]:
                self.enterOuterAlt(localctx, 6)
                self.state = 108
                self.match(SQLParser.EOF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def connectjdbc(self):
            return self.getTypedRuleContext(SQLParser.ConnectjdbcContext,0)


        def connectlocal(self):
            return self.getTypedRuleContext(SQLParser.ConnectlocalContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_connect

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnect" ):
                return visitor.visitConnect(self)
            else:
                return visitor.visitChildren(self)




    def connect(self):

        localctx = SQLParser.ConnectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_connect)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.state = 111
                self.connectjdbc()
                pass

            elif la_ == 2:
                self.state = 112
                self.connectlocal()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectlocalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT(self):
            return self.getToken(SQLParser.CONNECT, 0)

        def CONNECT_SLASH(self):
            return self.getToken(SQLParser.CONNECT_SLASH, 0)

        def connectlocalService(self):
            return self.getTypedRuleContext(SQLParser.ConnectlocalServiceContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_connectlocal

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectlocal" ):
                return visitor.visitConnectlocal(self)
            else:
                return visitor.visitChildren(self)




    def connectlocal(self):

        localctx = SQLParser.ConnectlocalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_connectlocal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            self.match(SQLParser.CONNECT)
            self.state = 116
            self.match(SQLParser.CONNECT_SLASH)
            self.state = 117
            self.connectlocalService()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectjdbcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT(self):
            return self.getToken(SQLParser.CONNECT, 0)

        def connectUserInfo(self):
            return self.getTypedRuleContext(SQLParser.ConnectUserInfoContext,0)


        def connectDriver(self):
            return self.getTypedRuleContext(SQLParser.ConnectDriverContext,0)


        def CONNECT_COLON(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.CONNECT_COLON)
            else:
                return self.getToken(SQLParser.CONNECT_COLON, i)

        def connectDriverSchema(self):
            return self.getTypedRuleContext(SQLParser.ConnectDriverSchemaContext,0)


        def CONNECT_DASH(self):
            return self.getToken(SQLParser.CONNECT_DASH, 0)

        def connectHost(self):
            return self.getTypedRuleContext(SQLParser.ConnectHostContext,0)


        def connectService(self):
            return self.getTypedRuleContext(SQLParser.ConnectServiceContext,0)


        def CONNECT_QUESTION(self):
            return self.getToken(SQLParser.CONNECT_QUESTION, 0)

        def connectParameters(self):
            return self.getTypedRuleContext(SQLParser.ConnectParametersContext,0)


        def CONNECT_SLASH(self):
            return self.getToken(SQLParser.CONNECT_SLASH, 0)

        def CONNECT_AT(self):
            return self.getToken(SQLParser.CONNECT_AT, 0)

        def connectDriverType(self):
            return self.getTypedRuleContext(SQLParser.ConnectDriverTypeContext,0)


        def connectPort(self):
            return self.getTypedRuleContext(SQLParser.ConnectPortContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_connectjdbc

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectjdbc" ):
                return visitor.visitConnectjdbc(self)
            else:
                return visitor.visitChildren(self)




    def connectjdbc(self):

        localctx = SQLParser.ConnectjdbcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_connectjdbc)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 119
            self.match(SQLParser.CONNECT)

            self.state = 120
            self.connectUserInfo()
            self.state = 122
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==52:
                self.state = 121
                self.match(SQLParser.CONNECT_AT)


            self.state = 141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==61:
                self.state = 124
                self.connectDriver()
                self.state = 125
                self.match(SQLParser.CONNECT_COLON)
                self.state = 126
                self.connectDriverSchema()
                self.state = 127
                self.match(SQLParser.CONNECT_COLON)
                self.state = 131
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==64:
                    self.state = 128
                    self.connectDriverType()
                    self.state = 129
                    self.match(SQLParser.CONNECT_COLON)


                self.state = 133
                self.match(SQLParser.CONNECT_DASH)
                self.state = 134
                self.connectHost()
                self.state = 136
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==63:
                    self.state = 135
                    self.connectPort()


                self.state = 138
                _la = self._input.LA(1)
                if not(_la==53 or _la==54):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 139
                self.connectService()


            self.state = 145
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==55:
                self.state = 143
                self.match(SQLParser.CONNECT_QUESTION)
                self.state = 144
                self.connectParameters()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectUserInfoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def connectUser(self):
            return self.getTypedRuleContext(SQLParser.ConnectUserContext,0)


        def CONNECT_SLASH(self):
            return self.getToken(SQLParser.CONNECT_SLASH, 0)

        def connectPassword(self):
            return self.getTypedRuleContext(SQLParser.ConnectPasswordContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_connectUserInfo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectUserInfo" ):
                return visitor.visitConnectUserInfo(self)
            else:
                return visitor.visitChildren(self)




    def connectUserInfo(self):

        localctx = SQLParser.ConnectUserInfoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_connectUserInfo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 147
            self.connectUser()
            self.state = 150
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==53:
                self.state = 148
                self.match(SQLParser.CONNECT_SLASH)
                self.state = 149
                self.connectPassword()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectDriverContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def JDBC(self):
            return self.getToken(SQLParser.JDBC, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectDriver

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectDriver" ):
                return visitor.visitConnectDriver(self)
            else:
                return visitor.visitChildren(self)




    def connectDriver(self):

        localctx = SQLParser.ConnectDriverContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_connectDriver)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 152
            self.match(SQLParser.JDBC)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectDriverSchemaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectDriverSchema

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectDriverSchema" ):
                return visitor.visitConnectDriverSchema(self)
            else:
                return visitor.visitChildren(self)




    def connectDriverSchema(self):

        localctx = SQLParser.ConnectDriverSchemaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_connectDriverSchema)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 154
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectDriverTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectDriverType

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectDriverType" ):
                return visitor.visitConnectDriverType(self)
            else:
                return visitor.visitChildren(self)




    def connectDriverType(self):

        localctx = SQLParser.ConnectDriverTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_connectDriverType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 156
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectHostContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IPV4(self):
            return self.getToken(SQLParser.IPV4, 0)

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectHost

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectHost" ):
                return visitor.visitConnectHost(self)
            else:
                return visitor.visitChildren(self)




    def connectHost(self):

        localctx = SQLParser.ConnectHostContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_connectHost)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 158
            _la = self._input.LA(1)
            if not(_la==62 or _la==64):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectUserContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectUser

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectUser" ):
                return visitor.visitConnectUser(self)
            else:
                return visitor.visitChildren(self)




    def connectUser(self):

        localctx = SQLParser.ConnectUserContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_connectUser)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectPasswordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectPassword

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectPassword" ):
                return visitor.visitConnectPassword(self)
            else:
                return visitor.visitChildren(self)




    def connectPassword(self):

        localctx = SQLParser.ConnectPasswordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_connectPassword)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectPortContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_PORT(self):
            return self.getToken(SQLParser.CONNECT_PORT, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectPort

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectPort" ):
                return visitor.visitConnectPort(self)
            else:
                return visitor.visitChildren(self)




    def connectPort(self):

        localctx = SQLParser.ConnectPortContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_connectPort)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 164
            self.match(SQLParser.CONNECT_PORT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectServiceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.CONNECT_STRING)
            else:
                return self.getToken(SQLParser.CONNECT_STRING, i)

        def CONNECT_COLON(self):
            return self.getToken(SQLParser.CONNECT_COLON, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectService

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectService" ):
                return visitor.visitConnectService(self)
            else:
                return visitor.visitChildren(self)




    def connectService(self):

        localctx = SQLParser.ConnectServiceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_connectService)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 166
            self.match(SQLParser.CONNECT_STRING)
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==54:
                self.state = 167
                self.match(SQLParser.CONNECT_COLON)
                self.state = 168
                self.match(SQLParser.CONNECT_STRING)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectlocalServiceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectlocalService

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectlocalService" ):
                return visitor.visitConnectlocalService(self)
            else:
                return visitor.visitChildren(self)




    def connectlocalService(self):

        localctx = SQLParser.ConnectlocalServiceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_connectlocalService)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 171
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectParameterNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectParameterName

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectParameterName" ):
                return visitor.visitConnectParameterName(self)
            else:
                return visitor.visitChildren(self)




    def connectParameterName(self):

        localctx = SQLParser.ConnectParameterNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_connectParameterName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 173
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectParameterValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONNECT_STRING(self):
            return self.getToken(SQLParser.CONNECT_STRING, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_connectParameterValue

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectParameterValue" ):
                return visitor.visitConnectParameterValue(self)
            else:
                return visitor.visitChildren(self)




    def connectParameterValue(self):

        localctx = SQLParser.ConnectParameterValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_connectParameterValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.match(SQLParser.CONNECT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectParameterContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def connectParameterName(self):
            return self.getTypedRuleContext(SQLParser.ConnectParameterNameContext,0)


        def CONNECT_EQUAL(self):
            return self.getToken(SQLParser.CONNECT_EQUAL, 0)

        def connectParameterValue(self):
            return self.getTypedRuleContext(SQLParser.ConnectParameterValueContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_connectParameter

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectParameter" ):
                return visitor.visitConnectParameter(self)
            else:
                return visitor.visitChildren(self)




    def connectParameter(self):

        localctx = SQLParser.ConnectParameterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_connectParameter)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 177
            self.connectParameterName()
            self.state = 178
            self.match(SQLParser.CONNECT_EQUAL)
            self.state = 179
            self.connectParameterValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConnectParametersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def connectParameter(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SQLParser.ConnectParameterContext)
            else:
                return self.getTypedRuleContext(SQLParser.ConnectParameterContext,i)


        def CONNECT_PARA_AND(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.CONNECT_PARA_AND)
            else:
                return self.getToken(SQLParser.CONNECT_PARA_AND, i)

        def getRuleIndex(self):
            return SQLParser.RULE_connectParameters

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConnectParameters" ):
                return visitor.visitConnectParameters(self)
            else:
                return visitor.visitChildren(self)




    def connectParameters(self):

        localctx = SQLParser.ConnectParametersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_connectParameters)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 181
            self.connectParameter()
            self.state = 188
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==60:
                self.state = 184 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 182
                    self.match(SQLParser.CONNECT_PARA_AND)
                    self.state = 183
                    self.connectParameter()
                    self.state = 186 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==60):
                        break



        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DisconnectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DISCONNECT(self):
            return self.getToken(SQLParser.DISCONNECT, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(SQLParser.ExpressionContext,i)


        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.INT)
            else:
                return self.getToken(SQLParser.INT, i)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_disconnect

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDisconnect" ):
                return visitor.visitDisconnect(self)
            else:
                return visitor.visitChildren(self)




    def disconnect(self):

        localctx = SQLParser.DisconnectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_disconnect)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.match(SQLParser.DISCONNECT)
            self.state = 195
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((_la) & ~0x3f) == 0 and ((1 << _la) & 1407377027891200) != 0:
                self.state = 193
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 50]:
                    self.state = 191
                    self.expression()
                    pass
                elif token in [48]:
                    self.state = 192
                    self.match(SQLParser.INT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 197
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 199
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 198
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SessionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SESSION(self):
            return self.getToken(SQLParser.SESSION, 0)

        def SESSION_SAVE(self):
            return self.getToken(SQLParser.SESSION_SAVE, 0)

        def SESSION_RELEASE(self):
            return self.getToken(SQLParser.SESSION_RELEASE, 0)

        def SESSION_RESTORE(self):
            return self.getToken(SQLParser.SESSION_RESTORE, 0)

        def SESSION_SAVEURL(self):
            return self.getToken(SQLParser.SESSION_SAVEURL, 0)

        def SESSION_SHOW(self):
            return self.getToken(SQLParser.SESSION_SHOW, 0)

        def SESSION_NAME(self):
            return self.getToken(SQLParser.SESSION_NAME, 0)

        def SESSION_END(self):
            return self.getToken(SQLParser.SESSION_END, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_session

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSession" ):
                return visitor.visitSession(self)
            else:
                return visitor.visitChildren(self)




    def session(self):

        localctx = SQLParser.SessionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_session)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 201
            self.match(SQLParser.SESSION)
            self.state = 202
            _la = self._input.LA(1)
            if not((((_la - 71)) & ~0x3f) == 0 and ((1 << (_la - 71)) & 31) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 204
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==76:
                self.state = 203
                self.match(SQLParser.SESSION_NAME)


            self.state = 207
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==77:
                self.state = 206
                self.match(SQLParser.SESSION_END)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def String(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.String)
            else:
                return self.getToken(SQLParser.String, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.DOT)
            else:
                return self.getToken(SQLParser.DOT, i)

        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.COLON)
            else:
                return self.getToken(SQLParser.COLON, i)

        def SLASH(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.SLASH)
            else:
                return self.getToken(SQLParser.SLASH, i)

        def BRACKET_OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.BRACKET_OPEN)
            else:
                return self.getToken(SQLParser.BRACKET_OPEN, i)

        def BRACKET_CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.BRACKET_CLOSE)
            else:
                return self.getToken(SQLParser.BRACKET_CLOSE, i)

        def ESCAPE(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.ESCAPE)
            else:
                return self.getToken(SQLParser.ESCAPE, i)

        def SQUARE_OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.SQUARE_OPEN)
            else:
                return self.getToken(SQLParser.SQUARE_OPEN, i)

        def SQUARE_CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.SQUARE_CLOSE)
            else:
                return self.getToken(SQLParser.SQUARE_CLOSE, i)

        def DOUBLE_QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.DOUBLE_QUOTE)
            else:
                return self.getToken(SQLParser.DOUBLE_QUOTE, i)

        def SINGLE_QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.SINGLE_QUOTE)
            else:
                return self.getToken(SQLParser.SINGLE_QUOTE, i)

        def getRuleIndex(self):
            return SQLParser.RULE_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = SQLParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 210 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 209
                    _la = self._input.LA(1)
                    if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 1125902051180544) != 0):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 212 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sqlCreate(self):
            return self.getTypedRuleContext(SQLParser.SqlCreateContext,0)


        def sqlReplace(self):
            return self.getTypedRuleContext(SQLParser.SqlReplaceContext,0)


        def sqlInsert(self):
            return self.getTypedRuleContext(SQLParser.SqlInsertContext,0)


        def sqlUpdate(self):
            return self.getTypedRuleContext(SQLParser.SqlUpdateContext,0)


        def sqlDelete(self):
            return self.getTypedRuleContext(SQLParser.SqlDeleteContext,0)


        def sqlSelect(self):
            return self.getTypedRuleContext(SQLParser.SqlSelectContext,0)


        def sqlDeclare(self):
            return self.getTypedRuleContext(SQLParser.SqlDeclareContext,0)


        def sqlDrop(self):
            return self.getTypedRuleContext(SQLParser.SqlDropContext,0)


        def sqlCommitRollback(self):
            return self.getTypedRuleContext(SQLParser.SqlCommitRollbackContext,0)


        def sqlCreateProcedure(self):
            return self.getTypedRuleContext(SQLParser.SqlCreateProcedureContext,0)


        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sql

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSql" ):
                return visitor.visitSql(self)
            else:
                return visitor.visitChildren(self)




    def sql(self):

        localctx = SQLParser.SqlContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_sql)
        try:
            self.state = 225
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5]:
                self.enterOuterAlt(localctx, 1)
                self.state = 214
                self.sqlCreate()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 2)
                self.state = 215
                self.sqlReplace()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 3)
                self.state = 216
                self.sqlInsert()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 4)
                self.state = 217
                self.sqlUpdate()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 5)
                self.state = 218
                self.sqlDelete()
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 6)
                self.state = 219
                self.sqlSelect()
                pass
            elif token in [11, 12]:
                self.enterOuterAlt(localctx, 7)
                self.state = 220
                self.sqlDeclare()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 8)
                self.state = 221
                self.sqlDrop()
                pass
            elif token in [14, 15]:
                self.enterOuterAlt(localctx, 9)
                self.state = 222
                self.sqlCommitRollback()
                pass
            elif token in [16]:
                self.enterOuterAlt(localctx, 10)
                self.state = 223
                self.sqlCreateProcedure()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 11)
                self.state = 224
                self.match(SQLParser.CRLF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlCreateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_CREATE(self):
            return self.getToken(SQLParser.SQL_CREATE, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlCreate

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlCreate" ):
                return visitor.visitSqlCreate(self)
            else:
                return visitor.visitChildren(self)




    def sqlCreate(self):

        localctx = SQLParser.SqlCreateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_sqlCreate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 227
            self.match(SQLParser.SQL_CREATE)
            self.state = 228
            self.match(SQLParser.SQL_END)
            self.state = 230
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 229
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlReplaceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_REPLACE(self):
            return self.getToken(SQLParser.SQL_REPLACE, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlReplace

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlReplace" ):
                return visitor.visitSqlReplace(self)
            else:
                return visitor.visitChildren(self)




    def sqlReplace(self):

        localctx = SQLParser.SqlReplaceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_sqlReplace)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 232
            self.match(SQLParser.SQL_REPLACE)
            self.state = 233
            self.match(SQLParser.SQL_END)
            self.state = 235
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 234
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlInsertContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_INSERT(self):
            return self.getToken(SQLParser.SQL_INSERT, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlInsert

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlInsert" ):
                return visitor.visitSqlInsert(self)
            else:
                return visitor.visitChildren(self)




    def sqlInsert(self):

        localctx = SQLParser.SqlInsertContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_sqlInsert)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 237
            self.match(SQLParser.SQL_INSERT)
            self.state = 238
            self.match(SQLParser.SQL_END)
            self.state = 240
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 239
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlUpdateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_UPDATE(self):
            return self.getToken(SQLParser.SQL_UPDATE, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlUpdate

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlUpdate" ):
                return visitor.visitSqlUpdate(self)
            else:
                return visitor.visitChildren(self)




    def sqlUpdate(self):

        localctx = SQLParser.SqlUpdateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_sqlUpdate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 242
            self.match(SQLParser.SQL_UPDATE)
            self.state = 243
            self.match(SQLParser.SQL_END)
            self.state = 245
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 244
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlDeleteContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_DELETE(self):
            return self.getToken(SQLParser.SQL_DELETE, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlDelete

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlDelete" ):
                return visitor.visitSqlDelete(self)
            else:
                return visitor.visitChildren(self)




    def sqlDelete(self):

        localctx = SQLParser.SqlDeleteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_sqlDelete)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 247
            self.match(SQLParser.SQL_DELETE)
            self.state = 248
            self.match(SQLParser.SQL_END)
            self.state = 250
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 249
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlSelectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_SELECT(self):
            return self.getToken(SQLParser.SQL_SELECT, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlSelect

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlSelect" ):
                return visitor.visitSqlSelect(self)
            else:
                return visitor.visitChildren(self)




    def sqlSelect(self):

        localctx = SQLParser.SqlSelectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_sqlSelect)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 252
            self.match(SQLParser.SQL_SELECT)
            self.state = 253
            self.match(SQLParser.SQL_END)
            self.state = 255
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 254
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlDropContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_DROP(self):
            return self.getToken(SQLParser.SQL_DROP, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlDrop

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlDrop" ):
                return visitor.visitSqlDrop(self)
            else:
                return visitor.visitChildren(self)




    def sqlDrop(self):

        localctx = SQLParser.SqlDropContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_sqlDrop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 257
            self.match(SQLParser.SQL_DROP)
            self.state = 258
            self.match(SQLParser.SQL_END)
            self.state = 260
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 259
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlCommitRollbackContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_COMMIT(self):
            return self.getToken(SQLParser.SQL_COMMIT, 0)

        def SQL_ROLLBACK(self):
            return self.getToken(SQLParser.SQL_ROLLBACK, 0)

        def SQL_END(self):
            return self.getToken(SQLParser.SQL_END, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlCommitRollback

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlCommitRollback" ):
                return visitor.visitSqlCommitRollback(self)
            else:
                return visitor.visitChildren(self)




    def sqlCommitRollback(self):

        localctx = SQLParser.SqlCommitRollbackContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_sqlCommitRollback)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 262
            _la = self._input.LA(1)
            if not(_la==14 or _la==15):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 264
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==80:
                self.state = 263
                self.match(SQLParser.SQL_END)


            self.state = 267
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 266
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlDeclareContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_SLASH(self):
            return self.getToken(SQLParser.SQL_SLASH, 0)

        def SQL_DECLARE(self):
            return self.getToken(SQLParser.SQL_DECLARE, 0)

        def SQL_BEGIN(self):
            return self.getToken(SQLParser.SQL_BEGIN, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlDeclare

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlDeclare" ):
                return visitor.visitSqlDeclare(self)
            else:
                return visitor.visitChildren(self)




    def sqlDeclare(self):

        localctx = SQLParser.SqlDeclareContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_sqlDeclare)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 269
            _la = self._input.LA(1)
            if not(_la==11 or _la==12):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 270
            self.match(SQLParser.SQL_SLASH)
            self.state = 272
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 271
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SqlCreateProcedureContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SQL_CREATE_PROCEDURE(self):
            return self.getToken(SQLParser.SQL_CREATE_PROCEDURE, 0)

        def SQL_SLASH(self):
            return self.getToken(SQLParser.SQL_SLASH, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sqlCreateProcedure

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSqlCreateProcedure" ):
                return visitor.visitSqlCreateProcedure(self)
            else:
                return visitor.visitChildren(self)




    def sqlCreateProcedure(self):

        localctx = SQLParser.SqlCreateProcedureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_sqlCreateProcedure)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 274
            self.match(SQLParser.SQL_CREATE_PROCEDURE)
            self.state = 275
            self.match(SQLParser.SQL_SLASH)
            self.state = 277
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 276
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BaseCommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assert_(self):
            return self.getTypedRuleContext(SQLParser.AssertContext,0)


        def load(self):
            return self.getTypedRuleContext(SQLParser.LoadContext,0)


        def host(self):
            return self.getTypedRuleContext(SQLParser.HostContext,0)


        def start(self):
            return self.getTypedRuleContext(SQLParser.StartContext,0)


        def loop(self):
            return self.getTypedRuleContext(SQLParser.LoopContext,0)


        def if_(self):
            return self.getTypedRuleContext(SQLParser.IfContext,0)


        def endif(self):
            return self.getTypedRuleContext(SQLParser.EndifContext,0)


        def whenever(self):
            return self.getTypedRuleContext(SQLParser.WheneverContext,0)


        def set_(self):
            return self.getTypedRuleContext(SQLParser.SetContext,0)


        def use(self):
            return self.getTypedRuleContext(SQLParser.UseContext,0)


        def exit(self):
            return self.getTypedRuleContext(SQLParser.ExitContext,0)


        def quit(self):
            return self.getTypedRuleContext(SQLParser.QuitContext,0)


        def sleep(self):
            return self.getTypedRuleContext(SQLParser.SleepContext,0)


        def spool(self):
            return self.getTypedRuleContext(SQLParser.SpoolContext,0)


        def script(self):
            return self.getTypedRuleContext(SQLParser.ScriptContext,0)


        def echo(self):
            return self.getTypedRuleContext(SQLParser.EchoContext,0)


        def getRuleIndex(self):
            return SQLParser.RULE_baseCommand

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBaseCommand" ):
                return visitor.visitBaseCommand(self)
            else:
                return visitor.visitChildren(self)




    def baseCommand(self):

        localctx = SQLParser.BaseCommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_baseCommand)
        try:
            self.state = 295
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [39]:
                self.enterOuterAlt(localctx, 1)
                self.state = 279
                self.assert_()
                pass
            elif token in [41]:
                self.enterOuterAlt(localctx, 2)
                self.state = 280
                self.load()
                pass
            elif token in [42]:
                self.enterOuterAlt(localctx, 3)
                self.state = 281
                self.host()
                pass
            elif token in [40]:
                self.enterOuterAlt(localctx, 4)
                self.state = 282
                self.start()
                pass
            elif token in [46]:
                self.enterOuterAlt(localctx, 5)
                self.state = 283
                self.loop()
                pass
            elif token in [43]:
                self.enterOuterAlt(localctx, 6)
                self.state = 284
                self.if_()
                pass
            elif token in [44]:
                self.enterOuterAlt(localctx, 7)
                self.state = 285
                self.endif()
                pass
            elif token in [47]:
                self.enterOuterAlt(localctx, 8)
                self.state = 286
                self.whenever()
                pass
            elif token in [45]:
                self.enterOuterAlt(localctx, 9)
                self.state = 287
                self.set_()
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 10)
                self.state = 288
                self.use()
                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 11)
                self.state = 289
                self.exit()
                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 12)
                self.state = 290
                self.quit()
                pass
            elif token in [35]:
                self.enterOuterAlt(localctx, 13)
                self.state = 291
                self.sleep()
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 14)
                self.state = 292
                self.spool()
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 15)
                self.state = 293
                self.script()
                pass
            elif token in [37]:
                self.enterOuterAlt(localctx, 16)
                self.state = 294
                self.echo()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXIT(self):
            return self.getToken(SQLParser.EXIT, 0)

        def INT(self):
            return self.getToken(SQLParser.INT, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_exit

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExit" ):
                return visitor.visitExit(self)
            else:
                return visitor.visitChildren(self)




    def exit(self):

        localctx = SQLParser.ExitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_exit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 297
            self.match(SQLParser.EXIT)
            self.state = 299
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==48:
                self.state = 298
                self.match(SQLParser.INT)


            self.state = 302
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 301
                self.match(SQLParser.SEMICOLON)


            self.state = 305
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 304
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUIT(self):
            return self.getToken(SQLParser.QUIT, 0)

        def INT(self):
            return self.getToken(SQLParser.INT, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_quit

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuit" ):
                return visitor.visitQuit(self)
            else:
                return visitor.visitChildren(self)




    def quit(self):

        localctx = SQLParser.QuitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_quit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            self.match(SQLParser.QUIT)
            self.state = 309
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==48:
                self.state = 308
                self.match(SQLParser.INT)


            self.state = 312
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 311
                self.match(SQLParser.SEMICOLON)


            self.state = 315
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 314
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def USE(self):
            return self.getToken(SQLParser.USE, 0)

        def USE_API(self):
            return self.getToken(SQLParser.USE_API, 0)

        def USE_SQL(self):
            return self.getToken(SQLParser.USE_SQL, 0)

        def USE_SEMICOLON(self):
            return self.getToken(SQLParser.USE_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_use

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUse" ):
                return visitor.visitUse(self)
            else:
                return visitor.visitChildren(self)




    def use(self):

        localctx = SQLParser.UseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_use)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 317
            self.match(SQLParser.USE)
            self.state = 318
            _la = self._input.LA(1)
            if not(_la==134 or _la==135):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 320
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==137:
                self.state = 319
                self.match(SQLParser.USE_SEMICOLON)


            self.state = 323
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 322
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SleepContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLEEP(self):
            return self.getToken(SQLParser.SLEEP, 0)

        def INT(self):
            return self.getToken(SQLParser.INT, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_sleep

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSleep" ):
                return visitor.visitSleep(self)
            else:
                return visitor.visitChildren(self)




    def sleep(self):

        localctx = SQLParser.SleepContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_sleep)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 325
            self.match(SQLParser.SLEEP)
            self.state = 326
            self.match(SQLParser.INT)
            self.state = 328
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 327
                self.match(SQLParser.SEMICOLON)


            self.state = 331
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 330
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StartContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def START(self):
            return self.getToken(SQLParser.START, 0)

        def START_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.START_EXPRESSION)
            else:
                return self.getToken(SQLParser.START_EXPRESSION, i)

        def START_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.START_COMMA)
            else:
                return self.getToken(SQLParser.START_COMMA, i)

        def START_LOOP(self):
            return self.getToken(SQLParser.START_LOOP, 0)

        def START_INT(self):
            return self.getToken(SQLParser.START_INT, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_start

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStart" ):
                return visitor.visitStart(self)
            else:
                return visitor.visitChildren(self)




    def start(self):

        localctx = SQLParser.StartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_start)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 333
            self.match(SQLParser.START)
            self.state = 334
            self.match(SQLParser.START_EXPRESSION)
            self.state = 339
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==101:
                self.state = 335
                self.match(SQLParser.START_COMMA)
                self.state = 336
                self.match(SQLParser.START_EXPRESSION)
                self.state = 341
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 343
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==99:
                self.state = 342
                self.match(SQLParser.START_LOOP)


            self.state = 346
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==100:
                self.state = 345
                self.match(SQLParser.START_INT)


            self.state = 349
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 348
                self.match(SQLParser.SEMICOLON)


            self.state = 352
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 351
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoadContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOAD(self):
            return self.getToken(SQLParser.LOAD, 0)

        def LOAD_OPTION(self):
            return self.getToken(SQLParser.LOAD_OPTION, 0)

        def LOAD_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.LOAD_EXPRESSION)
            else:
                return self.getToken(SQLParser.LOAD_EXPRESSION, i)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_load

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoad" ):
                return visitor.visitLoad(self)
            else:
                return visitor.visitChildren(self)




    def load(self):

        localctx = SQLParser.LoadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_load)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 354
            self.match(SQLParser.LOAD)
            self.state = 355
            self.match(SQLParser.LOAD_OPTION)
            self.state = 357 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 356
                self.match(SQLParser.LOAD_EXPRESSION)
                self.state = 359 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==96):
                    break

            self.state = 362
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 361
                self.match(SQLParser.SEMICOLON)


            self.state = 365
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 364
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssertContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSERT(self):
            return self.getToken(SQLParser.ASSERT, 0)

        def ASSERT_EXPRESSION(self):
            return self.getToken(SQLParser.ASSERT_EXPRESSION, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_assert

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssert" ):
                return visitor.visitAssert(self)
            else:
                return visitor.visitChildren(self)




    def assert_(self):

        localctx = SQLParser.AssertContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_assert)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 367
            self.match(SQLParser.ASSERT)
            self.state = 368
            self.match(SQLParser.ASSERT_EXPRESSION)
            self.state = 370
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 369
                self.match(SQLParser.SEMICOLON)


            self.state = 373
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 372
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HostContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HOST(self):
            return self.getToken(SQLParser.HOST, 0)

        def HOST_BLOCK(self):
            return self.getToken(SQLParser.HOST_BLOCK, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_host

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHost" ):
                return visitor.visitHost(self)
            else:
                return visitor.visitChildren(self)




    def host(self):

        localctx = SQLParser.HostContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_host)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 375
            self.match(SQLParser.HOST)
            self.state = 376
            self.match(SQLParser.HOST_BLOCK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOOP(self):
            return self.getToken(SQLParser.LOOP, 0)

        def LOOP_BREAK(self):
            return self.getToken(SQLParser.LOOP_BREAK, 0)

        def LOOP_END(self):
            return self.getToken(SQLParser.LOOP_END, 0)

        def LOOP_CONTINUE(self):
            return self.getToken(SQLParser.LOOP_CONTINUE, 0)

        def LOOP_BEGIN(self):
            return self.getToken(SQLParser.LOOP_BEGIN, 0)

        def LOOP_UNTIL(self):
            return self.getToken(SQLParser.LOOP_UNTIL, 0)

        def LOOP_EXPRESSION(self):
            return self.getToken(SQLParser.LOOP_EXPRESSION, 0)

        def LOOP_SEMICOLON(self):
            return self.getToken(SQLParser.LOOP_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_loop

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoop" ):
                return visitor.visitLoop(self)
            else:
                return visitor.visitChildren(self)




    def loop(self):

        localctx = SQLParser.LoopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_loop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 378
            self.match(SQLParser.LOOP)
            self.state = 385
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [117]:
                self.state = 379
                self.match(SQLParser.LOOP_BREAK)
                pass
            elif token in [118]:
                self.state = 380
                self.match(SQLParser.LOOP_END)
                pass
            elif token in [119]:
                self.state = 381
                self.match(SQLParser.LOOP_CONTINUE)
                pass
            elif token in [113]:
                self.state = 382
                self.match(SQLParser.LOOP_BEGIN)
                self.state = 383
                self.match(SQLParser.LOOP_UNTIL)
                self.state = 384
                self.match(SQLParser.LOOP_EXPRESSION)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 388
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==111:
                self.state = 387
                self.match(SQLParser.LOOP_SEMICOLON)


            self.state = 391
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 390
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(SQLParser.IF, 0)

        def IF_EXPRESSION(self):
            return self.getToken(SQLParser.IF_EXPRESSION, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_if

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIf" ):
                return visitor.visitIf(self)
            else:
                return visitor.visitChildren(self)




    def if_(self):

        localctx = SQLParser.IfContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_if)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 393
            self.match(SQLParser.IF)
            self.state = 394
            self.match(SQLParser.IF_EXPRESSION)
            self.state = 396
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 395
                self.match(SQLParser.SEMICOLON)


            self.state = 399
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 398
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EndifContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENDIF(self):
            return self.getToken(SQLParser.ENDIF, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_endif

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndif" ):
                return visitor.visitEndif(self)
            else:
                return visitor.visitChildren(self)




    def endif(self):

        localctx = SQLParser.EndifContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_endif)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 401
            self.match(SQLParser.ENDIF)
            self.state = 403
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 402
                self.match(SQLParser.SEMICOLON)


            self.state = 406
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 405
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WheneverContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHENEVER(self):
            return self.getToken(SQLParser.WHENEVER, 0)

        def WHENEVER_ERROR(self):
            return self.getToken(SQLParser.WHENEVER_ERROR, 0)

        def WHENEVER_CONTINUE(self):
            return self.getToken(SQLParser.WHENEVER_CONTINUE, 0)

        def WHENEVER_SEMICOLON(self):
            return self.getToken(SQLParser.WHENEVER_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def WHENEVER_EXIT(self):
            return self.getToken(SQLParser.WHENEVER_EXIT, 0)

        def WHENEVER_EXITCODE(self):
            return self.getToken(SQLParser.WHENEVER_EXITCODE, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_whenever

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhenever" ):
                return visitor.visitWhenever(self)
            else:
                return visitor.visitChildren(self)




    def whenever(self):

        localctx = SQLParser.WheneverContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_whenever)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 408
            self.match(SQLParser.WHENEVER)
            self.state = 409
            self.match(SQLParser.WHENEVER_ERROR)
            self.state = 413
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [126]:
                self.state = 410
                self.match(SQLParser.WHENEVER_CONTINUE)
                pass
            elif token in [127]:
                self.state = 411
                self.match(SQLParser.WHENEVER_EXIT)
                self.state = 412
                self.match(SQLParser.WHENEVER_EXITCODE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 416
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==125:
                self.state = 415
                self.match(SQLParser.WHENEVER_SEMICOLON)


            self.state = 419
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 418
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpoolContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SPOOL(self):
            return self.getToken(SQLParser.SPOOL, 0)

        def String(self):
            return self.getToken(SQLParser.String, 0)

        def SEMICOLON(self):
            return self.getToken(SQLParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_spool

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpool" ):
                return visitor.visitSpool(self)
            else:
                return visitor.visitChildren(self)




    def spool(self):

        localctx = SQLParser.SpoolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_spool)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 421
            self.match(SQLParser.SPOOL)
            self.state = 422
            self.match(SQLParser.String)
            self.state = 424
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 423
                self.match(SQLParser.SEMICOLON)


            self.state = 427
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 426
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EchoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ECHO_OPEN(self):
            return self.getToken(SQLParser.ECHO_OPEN, 0)

        def EchoBlock(self):
            return self.getToken(SQLParser.EchoBlock, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def EOF(self):
            return self.getToken(SQLParser.EOF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_echo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEcho" ):
                return visitor.visitEcho(self)
            else:
                return visitor.visitChildren(self)




    def echo(self):

        localctx = SQLParser.EchoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_echo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 429
            self.match(SQLParser.ECHO_OPEN)
            self.state = 430
            self.match(SQLParser.EchoBlock)
            self.state = 432
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,62,self._ctx)
            if la_ == 1:
                self.state = 431
                _la = self._input.LA(1)
                if not(_la==-1 or _la==17):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ScriptContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SCRIPT_OPEN(self):
            return self.getToken(SQLParser.SCRIPT_OPEN, 0)

        def ScriptBlock(self):
            return self.getToken(SQLParser.ScriptBlock, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_script

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitScript" ):
                return visitor.visitScript(self)
            else:
                return visitor.visitChildren(self)




    def script(self):

        localctx = SQLParser.ScriptContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_script)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 434
            self.match(SQLParser.SCRIPT_OPEN)
            self.state = 435
            self.match(SQLParser.ScriptBlock)
            self.state = 437
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 436
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SET(self):
            return self.getToken(SQLParser.SET, 0)

        def SET_AT(self):
            return self.getToken(SQLParser.SET_AT, 0)

        def SET_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(SQLParser.SET_EXPRESSION)
            else:
                return self.getToken(SQLParser.SET_EXPRESSION, i)

        def SET_SEMICOLON(self):
            return self.getToken(SQLParser.SET_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(SQLParser.CRLF, 0)

        def getRuleIndex(self):
            return SQLParser.RULE_set

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSet" ):
                return visitor.visitSet(self)
            else:
                return visitor.visitChildren(self)




    def set_(self):

        localctx = SQLParser.SetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_set)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 439
            self.match(SQLParser.SET)
            self.state = 441
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==132:
                self.state = 440
                self.match(SQLParser.SET_AT)


            self.state = 446
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==130:
                self.state = 443
                self.match(SQLParser.SET_EXPRESSION)
                self.state = 448
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 450
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==131:
                self.state = 449
                self.match(SQLParser.SET_SEMICOLON)


            self.state = 453
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 452
                self.match(SQLParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





