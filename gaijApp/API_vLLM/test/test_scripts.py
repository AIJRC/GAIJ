" script with test scripts and controls "
import os 
import sys

def check_words(field,list_items):
    unwanted_words =["100%","brønnøysundregistrene","lederskap","styremedlemmer","ledende","leder","daglig leder","styrets leder","ledelsen","styreleder","styremedlem"]
    if field =='leadership':
        if list_items is not None and list_items:
            try:
                list_items = [item.lower() for item in list_items]
            except TypeError:
                print(list_items,type(list_items),(type(list_items)== 'NoneType') == False)
                sys.exit(1)
            if len(list(set(list_items) & set(unwanted_words)))>0:
                print(f"WARNING WARNING WARNING"'{list_items}')
                # save a file 
                file_path = os.path.dirname(__file__,'warningtext.txt')
                # check if it exists 
                if file_path.is_file():
                    # update it 
                    with open(file_path,'r') as f:
                        old_content = f.read()
                    new_content =  old_content + "\n" + "\n".join(list_items)
                    with open(file_path,'w') as f:
                        f.write(new_content)
                    # else write it 
                else:
                    with open(file_path,'w') as f:
                        f.write("\n".join(list_items))
                
                
        