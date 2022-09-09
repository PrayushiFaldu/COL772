
# IMPORTS
import json
import re
import copy
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("--input_path")
parser.add_argument("--solution_path")
args = parser.parse_args()


f = open(args.input_path,'r')
input_data = json.load(f)


# RULES

# PERFECT when punct is alone.
punct_ascii = [33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,58,59,60,61,62,63,64,91,92,93,94,95,96,123,124,125,126,45,126,173,1418,1470,5120,6150,8208,8209,8210,8211,8212,8213,8275,8315,8331,8722,11799,11834,11835,12316,12336,12448,65073,65074,65112,65123,65293,12448,65073,65074,65112,65123,65293]
def is_punct(val):
    if(ord(val) in punct_ascii):
        return True
    return False;

# if token is of length 1, then either it will be a number or punct else <self> - worked fine
number = {"1":"one", "2":"two", "3":"three", "4":"four", "5":"five", "6":"six", "7":"seven", "8":"eight", "9":"nine"}

def one_length_encoding(token):
    if(is_punct(token)):
        return "sil"
    return number.get(token,"<self>")


# tokens with only text -> romans and text
def only_alpha_encoding(token):
    res = list()
    for char in token:
        if(char.isalpha()):
            res.append(char.lower())
    return " ".join(res)
only_alpha_encoding("H. F.")


# # Numbers

# ## cardinals

def numToWords_2(num, is_date=False):
    num = num.strip()
    units = ['','one','two','three','four','five','six','seven','eight','nine']
    teens = ['','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
    tees = ['','ten','twenty','thirty','forty','fifty','sixty','seventy', 'eighty','ninety']
    thousands = ['','thousand','million','billion','trillion']
    res = []
    
    num = re.sub(r"[^0-9\-]","",num).strip()
    
    if(num[0] == '-'): 
        res.append("minus")
        num = num[1:]
        
    if (num in ["0","00","000"]): 
        res = ["zero"]
    
    else:
        num_string = str(num)
        groups = (int)((len(num_string)+2)/3)
        num_string = num_string.zfill(groups*3)
        num_partitions = [num_string[i:i + 3] for i in range(0, len(num_string), 3)]
        
        for part,nums in enumerate(num_partitions):
            a,b,c = (int)(nums[0]), (int)(nums[1]), (int)(nums[2])
            if(a) >= 1:
                res.extend([units[a],'hundred'])
            
            if(b >= 1 and c == 0):
                res.append(tees[b])
                
            if(b == 1 and c != 0):
                res.append(teens[c])
            
            if(b > 1 and c != 0):
                res.extend([tees[b],units[c]])
            
            if(b == 0 and c > 0):
                if(is_date):res.extend(['o',units[c]])
                else: res.append(units[c])
            
            res.append(thousands[groups-part-1])
                
    return ' '.join(res).strip()



# ## ISBN

isbn_to_word_nums = ['o','one','two','three','four','five','six','seven','eight','nine']

def isbn_to_word(isbn):
    isbn = isbn.strip()
    res = []
    for i in isbn:
        if(ord(i) < 48 or ord(i) > 57): 
            if(not(len(res)>0 and res[-1]=="sil")):
                res.append("sil")
        else: res.append(isbn_to_word_nums[ord(i)-48])
    
    result = " ".join(res)
    result = re.sub("\s{2,}"," ",result) 
    return result


# ## ORDINALS

ord_map = {"1":"first","2":"second","3":"third","5":"fifth", "12":"twelfth"}
def ordinals_to_word(num):
    num = num[:-2]
    
    if(ord_map.get(num)):
        return ord_map[num]
        
    num_words = numToWords_2(num)
    if(num_words[-1] == 'y'):
        return num_words[:-1]+"ieth"
    elif(num[-1] in list(ord_map.keys()) and (len(num)>=2 and num[-2] != '1')):
        return " ".join(num_words.split(" ")[:-1])+" "+ord_map[num[-1]]
    elif(num[-1]=='8'):
        return num_words+"h"
    else:
        return num_words+"th"



# ### DECIMALS

decimals_to_word_nums = ['zero','one','two','three','four','five','six','seven','eight','nine'] 
def decimals_to_word(num):
    num = num.strip()
    before_decimal = num.split(".")[0].strip()
    before_decimal = re.sub(r"[^0-9]","",before_decimal).strip()
    after_decimal = num.split(".")[1]
    res = numToWords_2(before_decimal)
    if (len(after_decimal) > 0):
        res = res + " point"
        for idx,i in enumerate(after_decimal):
            if(i=='0' and idx<len(after_decimal)-1): res = res + " o"
            else: res = res + " " + decimals_to_word_nums[ord(i) - 48]
    return res


# ## Numbers with comma

def number_with_comma_to_word(num):
    num = re.sub(r"[^0-9]+","",num)
    return numToWords_2(num)


# ## DATE

non_dig_regex = re.compile(r"[^0-9]+")
def text_date_to_word(date):
    date = date.strip()
    date_comp = date.split(" ")
    res = ""
    for idx, d in enumerate(date_comp):
        n = re.sub(r"[^0-9]+","",d)
        if(len(d)>0 and d[0].isalpha()):
            d = re.sub(r"[^A-Za-z]+","",d)
            res = res +" "+ d.lower()
        elif(len(n)<4):
            if(len(n)<=2): 
                n = n+"th"
            if(idx == 0): res = "the "+ ordinals_to_word(n) +" of"
            else: res = res +" "+ ordinals_to_word(n)
        elif(len(n)==4):
            if(n[-3:]=="000"):
                res = res + " "+numToWords_2(n[0:1]) +" thousand"
            elif(n[-2:]=="00"):
                res = res + " " +numToWords_2(n[0:2]) +" hundred"
            elif(int(n) < 2000 or int(n) >= 2010):
                res = res + " " +numToWords_2(n[0:2]) +" "+ numToWords_2(n[2:4], True)
            else:
                res = res + " " +numToWords_2(n) 
    
    res = re.sub("\s{2,}"," ",res)
    return res.strip()

std_date_format_regex = re.compile(r"^([0-9]{4}\-[0-9]{2}\-[0-9]{2}|[0-9]{2}\-[0-9]{2}\-[0-9]{4})$")
month_dict = {"01" : "january","02" : "february","03" : "march","04" : "april","05" : "may","06" : "june","07" : "july","08" : "august","09" : "september","10" : "october","11" : "november","12" : "december"}

def std_date_to_word(date):
    date_parts = date.split("-")
    type_tuple = (len(date_parts[0]), len(date_parts[1]), len(date_parts[2]))
    day = ""
    month=""
    year=""
    y =""
    
    if(type_tuple == (4,2,2)):
        day = ordinals_to_word(date_parts[2]+"th")
        month = month_dict.get(date_parts[1])
        y = date_parts[0]
    else:
        if((int)(date_parts[0]) > 12):
            day = ordinals_to_word(date_parts[0]+"th")
            month = month_dict.get(date_parts[1])
            y = date_parts[2]
        else:
            day = ordinals_to_word(date_parts[1]+"th")
            month = month_dict.get(date_parts[0])
            y = date_parts[2]
            
    if((int)(y) < 2000 or (int)(y) >= 2010):
        if(y[-3:]=="000"):
            year = numToWords_2(y[0:2]) +" thousand"
        elif(y[-2:]=="00"):
            year = numToWords_2(y[0:2]) +" hundred"
        else: 
            year = numToWords_2(y[0:2]) +" "+ numToWords_2(y[2:4], True)
    else:
        year = numToWords_2(y) 
        
    res = "the "+ day +" of "+month+" "+year
    res = re.sub("\s{2,}"," ",res)
    return res.strip()

# ### CURRENCY

currency_regex = re.compile(r"(?i)(£|\$|Rs|€)( |[0-9])")

currency = {"£" : "pound", "$" : "dollar", "rs" : "rupee", "€" : "euro"}
sub_currency = {"£" : "cent", "$" : "cent", "rs" : "paisa", "€" : "cent"}
currency_abbreviation = {"k" : "thousand", "m" : "million", "b" : "billion", "t" : "trillion", "cr" : "crore"}
def currency_to_word(num):
    num = num.lower()
    curr = re.compile(r"(?i)(£|\$|Rs|€)").search(num).group(1)
    curr_suffix_match = re.compile(r"(?i)cr|million|billion|trillion|m|b|t|k").search(num)
    num = re.sub(r"(?i)(£|\$|Rs|€)","",num)
    num = re.sub(r"(?i)cr|million|billion|trillion|m|b|t|k","",num)
    if("." in num):
        translated_curr = decimals_to_word(num)
        if(curr_suffix_match):
            translated_curr = translated_curr + " "+curr_suffix_match.group(0) + " "+ currency.get(curr)+"s"
        else:
            if(curr == "rs"):
                translated_curr = translated_curr.replace("point",f"rupees and")
                translated_curr += " paisa"
            else:
                translated_curr = translated_curr.replace("point",f"{currency.get(curr)}s and")
                translated_curr += " cents"
    else:
        num = re.sub(r"[^0-9]","",num)
        translated_curr = numToWords_2(num)
        if(curr_suffix_match):
            matched_suffix = curr_suffix_match.group(0)
            translated_curr = translated_curr + " "+currency_abbreviation.get(matched_suffix,matched_suffix) + " "+ currency.get(curr)+"s"
        else:
            translated_curr = translated_curr + " "+ currency.get(curr)+"s"
        
    return translated_curr




# ## numbers with unit

units = {"mm" : "millimeter", "cm" : "centimeter", "km" : "kilometer", "m" : "meter", "mi":"mile", "ha":"hectare", "in": "inch", "ft":"feet", "yd":"yard", "mg" : "milligram", "kg" : "kilogram", "g" : "gram", "db":"decible" }
units_regex = re.compile(r"\b([0-9]+ |[0-9]+)(\/|)(mm|cm|km|mi|m|ha|in|ft|yd|mg|kg|g|db)(2|3|²|³|)\b")
raised_to = {"2":"square","3":"cube","³" : "cube", "²" : "square"}

def number_with_units_to_word(num):
    org_num = num
    unit = units_regex.search(num).group(0)
    num = num.split("/")[0]
    unit = re.sub(r"[^A-Za-z]","",unit)
    num = re.sub(r"[A-Za-z](2|3|²|³|)","",num).strip()
    if("." in num): translated_num = decimals_to_word(num)
    else:
        num = re.sub(r"[^0-9]","",num).strip()
        translated_num = numToWords_2(num)
    if("/" in org_num):
        power = re.sub("[A-Za-z]+","",org_num.split("/")[1])
        translated_num = translated_num + " per "+ raised_to.get(power,"")+ " "+units.get(unit)
    else: 
        power = re.compile(r"(mm|cm|km|mi|m|ha|in|ft|yd|mg|kg|g|db)(2|3|²|³)").search(org_num)
        if(power):
            power = re.sub("[A-Za-z]+","",power.group(0))
            translated_num = translated_num + " "+raised_to.get(power,"")+" "+ units.get(unit) 
        else:
            translated_num = translated_num + " "+ units.get(unit)
    if(num != "1"):
        translated_num = translated_num + "s"
    return translated_num


# ## PARTS

parts_regex = re.compile(r"^(\-|)[0-9]+\/[0-9]+$")
part_dict = {"2":"half","4":"quarter"}
def parts_to_word(num):
    if(num in part_dict): return part_dict.get(num)
    part_1 = num.split("/")[0].strip()
    part_2 = num.split("/")[1].strip()
    
    if(part_2 in part_dict):
        if(part_1 == "1"):
            return  part_dict.get(part_2)
        else:
            return numToWords_2(part_1) +" "+  part_dict.get(part_2)+"s"
    else:
        if(part_1=="1" and len(part_2) == 1):
                translated_num = numToWords_2(part_1) +" "+  ordinals_to_word(part_2+"th")
        else:
            translated_num = numToWords_2(part_1) +" "+  ordinals_to_word(part_2+"th")+"s"
    return translated_num

mixed_parts_regex = re.compile(r"^(\-|)([0-9]+ )([0-9]+\/[0-9]+)$")
def mixed_parts_to_word(num):
    num = num.strip()
    part1 = numToWords_2(num.split(" ")[0].strip())
    part2 = parts_to_word(num.split(" ")[1].strip())
    if(part2 in ["half","quarter"]):
        return part1 + " and a " + part2
    return part1 + " and " + part2
    

# ## TIME

time_am_pm = {"am" : "a m", "pm":"p m"}
time_zone_regex = re.compile(r"(?i)(IST|CST|EST|MST|PST|SGT|WET|EET|GMT|UTC)")
time_to_word_regex = re.compile(r"(?i)(([0-9]{1,2}:( |)[0-9]{2})|[0-9]+ (a(\.|)m(\.|)|p(\.|)(\.|)))")

time_am_pm = {"am" : "a m", "pm":"p m"}
time_zone_regex = re.compile(r"(?i)(IST|CST|EST|MST|PST|SGT|WET|EET|GMT|UTC)")
time_to_word_regex = re.compile(r"(?i)(([0-9]{1,2}:( |)[0-9]{2})|[0-9]+ (a(\.|)m(\.|)|p(\.|)(\.|)))")

def time_to_word(time):
    time = time.lower()
    only_time = re.sub(r"[^0-9:]","", time).strip()
    time_zone = time_zone_regex.search(time)
    time = time_zone_regex.sub("", time)
    am_pm = re.sub(r"[^A-Za-z]","",time).strip()
    time_parts = only_time.split(":")
    if(len(time_parts) == 1):
        translated_time = numToWords_2(time_parts[0])
    elif(len(time_parts) == 2):
        translated_time = numToWords_2(time_parts[0])
        if(not time_parts[1] in["0","00"]):
            translated_time = translated_time + " " +numToWords_2(time_parts[1])
        else:
            if(int(time_parts[0])>12 or int(time_parts[0])==0): translated_time = translated_time + " hundred"
            else: translated_time = translated_time + " o'clock"
    elif(len(time_parts)==3):
        translated_time= ""
        if(not time_parts[0] in ["0","00"]):
            translated_time = translated_time + " " +numToWords_2(time_parts[0]) + " hour"
            if(not time_parts[0] in ["1","01"]):
                translated_time = translated_time + "s"
        if(not time_parts[1] in ["0","00"]):
            translated_time = translated_time + " " +numToWords_2(time_parts[1]) + " minute"
            if(not time_parts[1] in ["1","01"]):
                translated_time = translated_time + "s"
        if(not time_parts[2] in ["0","00"]):
            if(translated_time.strip() == "") : translated_time = numToWords_2(time_parts[2]) + " second"
            else: translated_time = translated_time + " and " +numToWords_2(time_parts[2]) + " second"
            if(not time_parts[2] in ["1","01"]):
                translated_time = translated_time + "s"
            
    if(time_am_pm.get(am_pm,"") != ""):
        translated_time = translated_time.replace(" o'clock","")
        translated_time = translated_time.replace(" hundred","")
        translated_time = translated_time + " " + time_am_pm.get(am_pm)
        
    if(time_zone):
        translated_time = translated_time + " "+ " ".join(time_zone.group(0))
        
    return translated_time.strip()


# ### Bytes

byte_regex = re.compile(r"^([0-9]+(\.[0-9]+|))( |)(KB|kb|MB|Mb|GB|Gb|TB|Tb|PB|Pb|B|b)(|\/(s|sec|second))$")
byte_unit_dict = {"KB":"kilobyte","Kb":"kilobit","MB":"megabyte", "Mb" : "megabit", "GB":"gigabyte", "Gb" : "gigabit","PB":"pentabyte", "Pb" : "pentabit", "B":"byte", "b" : "bit"}

def bytes_to_word(byte):
    unit = re.sub(r"[^A-Za-z\/]","",byte).strip()
    is_persec = re.compile(r"\/(second|sec|s)").search(unit)
    unit = re.sub(r"\/(second|sec|s)","",unit)
    num = re.sub(r"[^0-9\.]","",byte).strip()
    if("." in num):
        translated_byte = decimals_to_word(num)
    else:
        translated_byte = numToWords_2(num)
    
    translated_byte = translated_byte + " " +byte_unit_dict.get(unit)
    if (num!="1"): translated_byte += "s"
        
    if(is_persec):
        translated_byte = translated_byte + " per second" 
    
    return translated_byte



# ### ROMAN

roman_number_regex = re.compile(r"^(XL|XC|L{0,1}X{0,3})(IV|IX|V{0,1}I{0,3})$")
small_letter_regex = re.compile(r"^[a-z]")

def roman_to_text(roman, prev_token):
    
    roman_to_num_dict = {'I':1,'IV':4,'V':5,'IX':9,'X':10,'XL':40,'L':50,'XC':90}
    usual_words = ["Chapter","Topic", "Section", "Page"]
    cardinal_num = 0
    i = 0
    while(i < len(roman)):
        if(i+1 < len(roman) and roman_to_num_dict.get(roman[i:i+2],"") != ""):
            cardinal_num = cardinal_num + roman_to_num_dict.get(roman[i:i+2])
            i += 2
        else:
            cardinal_num = cardinal_num + roman_to_num_dict.get(roman[i])
            i += 1
            
    if(prev_token in usual_words or small_letter_regex.search(prev_token)):
        return numToWords_2(str(cardinal_num))
    else: return "the " + ordinals_to_word(str(cardinal_num)+"th")
    


date_with_month_regex = re.compile(r"(?i)\b(january|february|march|april|may|june|july|august|september|october|november|december)\b")
ordinals_regex = re.compile(r"[0-9]+(st|nd|th|rd)$")
# only_number_regex = re.compile(r"^(\-|)[0-9]+(\.[0-9]+|)$")
only_number_regex_2 = re.compile(r"^(\-|)[0-9]+(,[0-9]+|)(\.[0-9]+|)$")
number_with_comma_regex = re.compile(r"^[0-9]+,[0-9]+$")
percentage_regex = re.compile(r"[0-9]+( |)(%|pc|percent)$")
alphabet_regex = re.compile(r"[^A-Z]")
abbreviation_regex = re.compile(r"([A-Z](\.|\-))+")
replace_regex = re.compile(r"^[0-9\.]+( |)(thousand|million|billion|trillion|crore|millimeter|centimeter|kilometer|meter|mile|hectare|inch|feet|yard|milligram|kilogram|gram|decible|hour|second)(s|)$")

if __name__=="__main__":


    predicted = []
    temp_dict = {}
    for i in range(len(input_data)):
        temp = {}
        
        temp.update({"sid" : i})
        temp.update({"output_tokens" : []})
        for idx, pair in enumerate(zip(input_data[i]["input_tokens"], input_data[i]["input_tokens"])):

            try:
                temp["output_tokens"].append("<self>")
                p0 = pair[0].strip()
                # single punct
                if(len(p0)==1):
                    temp["output_tokens"][idx] = one_length_encoding(p0)

                # roman numbers
                elif(roman_number_regex.search(p0)):
                    prev_token = ""
                    if(idx-1 >=0): prev_token = input_data[i]["input_tokens"][idx-1]
                    temp["output_tokens"][idx] = roman_to_text(p0, prev_token)
                
                # quantity with units in text
                elif(replace_regex.search(p0)):
                    prefix = re.sub("[A-Za-z]","",p0).strip()
                    suffix = re.sub("[^A-Za-z]","",p0).strip()
                    if("." in p0):
                        temp["output_tokens"][idx] = decimals_to_word(prefix) + " " + suffix
                    else:
                        temp["output_tokens"][idx] = numToWords_2(prefix) + " " + suffix


                # contains only capital letters - romans
                elif(not alphabet_regex.search(p0.strip())):
                    temp["output_tokens"][idx] = only_alpha_encoding(p0)

                # abbreviations
                elif(abbreviation_regex.search(p0)):
                    temp["output_tokens"][idx] = only_alpha_encoding(p0)


                # ISBN - perfect
                elif(idx >0 and input_data[i]["input_tokens"][idx-1] == "ISBN"):
                    # print("yes")
                    temp["output_tokens"][idx] = isbn_to_word(p0)


                # Numbers - neg, decimal, years
                elif(only_number_regex_2.search(p0)):
                    numstr = str(p0)
                    if("." in p0):
                        temp["output_tokens"][idx] = decimals_to_word(p0)
                    elif(len(numstr) == 4):
                        if(numstr[-3:]=="000"):
                            temp["output_tokens"][idx] = numToWords_2(numstr[0:1]) +" thousand"
                        elif(numstr[-2:]=="00"):
                            temp["output_tokens"][idx] = numToWords_2(numstr[0:2]) +" hundred"
                        elif(int(p0) < 2000 or int(p0) >= 2010):
                            temp["output_tokens"][idx] = numToWords_2(numstr[0:2]) +" "+ numToWords_2(numstr[2:4], True)
                        else:
                            temp["output_tokens"][idx] = numToWords_2(p0) 
                    else:
                        temp["output_tokens"][idx] = numToWords_2(p0)     


                # Ordinals - perfect
                elif (ordinals_regex.search(p0)):
                    temp["output_tokens"][idx] = ordinals_to_word(p0)

                
                # Percentage - corner cases percent and pc
                elif(percentage_regex.search(p0)):
                    p0 = p0.replace("percent","%")
                    p0 = p0.replace("pc","%")
                    temp["output_tokens"][idx] = "none"
                    if("." in p0):
                        temp["output_tokens"][idx] = decimals_to_word(p0[:-1])+" percent"
                    else:
                        temp["output_tokens"][idx] = numToWords_2(p0[:-1])+" percent"

                
                # Date with text
                elif(date_with_month_regex.search(p0.strip())):
                        temp["output_tokens"][idx] = text_date_to_word(p0.strip())

                elif(std_date_format_regex.search(p0)):
                    temp["output_tokens"][idx] = std_date_to_word(p0)

                # currency
                elif(currency_regex.search(p0)):
                    temp["output_tokens"][idx] = currency_to_word(p0.strip())

                elif(units_regex.search(p0)):
                    temp["output_tokens"][idx] = number_with_units_to_word(p0.strip())

                elif(parts_regex.search(p0)):
                    temp["output_tokens"][idx] = parts_to_word(p0.strip())

                elif(mixed_parts_regex.search(p0)):
                    temp["output_tokens"][idx] = mixed_parts_to_word(p0.strip())

                elif(time_to_word_regex.search(p0.strip())):
                    temp["output_tokens"][idx] = time_to_word(p0.strip())

                elif(byte_regex.search(p0.strip())):
                    temp["output_tokens"][idx] = bytes_to_word(p0.strip())

                elif(not re.compile(r"[A-Za-z]").search(p0)):
                    temp["output_tokens"][idx] = isbn_to_word(p0)

            except Exception as e:
                pass
        
        predicted.append(temp)


with open(args.solution_path, "w") as f:
    json.dump(predicted, f, indent=4)
