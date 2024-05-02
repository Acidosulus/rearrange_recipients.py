import sqlalchemy
import urllib
from  stek import *
from Payroll import class_Payroll, Pay
from click import echo, style
import pandas as pd
import sys
import time
from rich import print


class Data_Store:
	def __init__(self):
		self.stek_agreemets_details = Get_list_of_agreements_details()

		file = open('prefixes_list.txt', "r", encoding='utf8')
		self.prefixes = []
		ll = file.readlines()
		ll1 = []
		ll2 =  []
		for i in range(len(ll)):
			lc = ll[i].replace('\n','').strip().lower()
			ll1.append(lc); ll1.append(lc.capitalize()); ll1.append(lc.upper())
		for i in range(len(ll1)):
			ll2.append(ll1[i])
			ll2.append(ll1[i]+' №'); ll2.append(ll1[i]+' N'); ll2.append(ll1[i]+' #'); ll2.append(ll1[i]+' M'); ll2.append(ll1[i]+' М')
			ll2.append(ll1[i]+'№'); ll2.append(ll1[i]+'N'); ll2.append(ll1[i]+'#'); ll2.append(ll1[i]+'M'); ll2.append(ll1[i]+'М')
		for el in ll2:
			self.prefixes.append(el); self.prefixes.append(el+' ')
		file.close()

# the function searches for the agreement number in the stack database and returns its details
def get_details_from_STEK_by_agreement_number(source_list:list, agreement_number:str) -> dict:
	ld_result = {'agreement':'', 'inn':'', 'kpp':'', 'name':''}
	for element in source_list:
		if element[0]==agreement_number:
			ld_result['agreement'] = element[0]; ld_result['inn'] = element[1]; ld_result['kpp'] = element[2]; ld_result['name'] = element[3]
			break
	return ld_result

# the function searches for the agreement number and inn/kpp and return result as dictionary
def get_details_by_purpose(ods:Data_Store, purpose:str, inn:str, kpp:str) -> dict:
	dict_result = {'agreement':'', 'inn':'', 'kpp':'', 'name':'', 'comment':'', 'agreement_by_inn':'', 'agreement_name_by_inn':''}
	lc_agreement = ''
	for prefix in ds.prefixes:
		if prefix in purpose:
			lc_agreement = purpose[purpose.find(prefix)+len(prefix):purpose.find(prefix)+len(prefix)+10]
			#print(f'"{prefix}"    {lc_agreement}')
			ld = get_details_from_STEK_by_agreement_number(ods.stek_agreemets_details, lc_agreement)
			if len(ld['agreement'])!=0:
				dict_result['agreement'] = ld['agreement']; dict_result['inn'] = ld['inn']; dict_result['kpp'] = ld['kpp']; dict_result['name'] = ld['name']
				dict_result['comment'] = f"""по префиксу "{prefix}" определен контрагент: №{dict_result['agreement']}, ИНН:{dict_result['inn']}, КПП:{dict_result['kpp']}, {dict_result['name']}"""
				break
	if len(dict_result['agreement'])==0:
		for stek_agreement in ods.stek_agreemets_details:
			if stek_agreement[0].strip() in purpose:
				dict_result['agreement'] = stek_agreement[0]; dict_result['inn'] = stek_agreement[1]; dict_result['kpp'] = stek_agreement[2]; dict_result['name'] = stek_agreement[3]
				dict_result['comment'] = f"""по вхождению номера договора "{stek_agreement[0].strip()}" определен контрагент: №{dict_result['agreement']}, ИНН:{dict_result['inn']}, КПП:{dict_result['kpp']}, {dict_result['name']}"""
	for i in range(len(ods.stek_agreemets_details)):
		#print(ods.stek_agreemets_details[1],'   ==    ', inn.strip())
		if ods.stek_agreemets_details[i][1]==inn.strip() and ods.stek_agreemets_details[i][2]==kpp.strip():
			dict_result['agreement_by_inn']=ods.stek_agreemets_details[i][0].strip(); dict_result['agreement_name_by_inn']=ods.stek_agreemets_details[i][3]
	if len(dict_result['agreement_by_inn'])==0:
		for i in range(len(ods.stek_agreemets_details)):
			if ods.stek_agreemets_details[i][1]==inn.strip():
				dict_result['agreement_by_inn']=ods.stek_agreemets_details[i][0]; dict_result['agreement_name_by_inn']=ods.stek_agreemets_details[i][3]
	return dict_result #get_details_by_purpose


ds = Data_Store()


payroll = class_Payroll(sys.argv[1])
payroll.Load_strings_from_file(payroll.path_to_source_file)
payroll.Parse_Strings_from_File()
ln_counter_unrecognized = 0
ln_counter_changed = 0
for pay in payroll.pays:
	lr = get_details_by_purpose(ds, pay.purpose, pay.inn, pay.kpp)
	if len(lr['inn'])!=0 and lr['inn']!=pay.inn:
		echo(style(f"{pay.inn}({lr['inn']})      {pay.purpose}", fg='bright_green'))
		ln_counter_changed += 1
	if len(lr['inn'])==0:
		ln_counter_unrecognized += 1
		echo(style(f"{pay.inn}({lr['inn']})      {pay.purpose}", fg='bright_blue'))
		print()
	pay.recognized = lr



ld_to_excel = {}
for pay in payroll.pays:
	echo(style(text=pay.recognized, fg='bright_green'))
	for st in pay.source:
		lc_key = st[0:st.find('=')]
		lc_value = st[st.find('=')+1:len(st)]
		if lc_key=='КодНазПлатежа':
			continue
		if lc_key not in ld_to_excel:
			ld_to_excel[lc_key] = [lc_value]
		else:
			ld_to_excel[lc_key].append(lc_value)
	if 'Распознанный номер договора' not in ld_to_excel:
		ld_to_excel['Распознанный номер договора']=[pay.recognized['agreement']]
	else:
		ld_to_excel['Распознанный номер договора'].append(pay.recognized['agreement'])
	
	if 'Название распознанного договора' not in ld_to_excel:
		ld_to_excel['Название распознанного договора']=[pay.recognized['name']]
	else:
		ld_to_excel['Название распознанного договора'].append(pay.recognized['name'])
	if 'Распознанный ИНН' not in ld_to_excel:
		ld_to_excel['Распознанный ИНН']=[pay.recognized['inn']]
	else:
		ld_to_excel['Распознанный ИНН'].append(pay.recognized['inn'])
	if 'Распознанный КПП' not in ld_to_excel:
		ld_to_excel['Распознанный КПП']=[pay.recognized['kpp']]
	else:
		ld_to_excel['Распознанный КПП'].append(pay.recognized['kpp'])
	if 'Комментарий' not in ld_to_excel:
		ld_to_excel['Комментарий']=[pay.recognized['comment']]
	else:
		ld_to_excel['Комментарий'].append(pay.recognized['comment'])
	if 'Распознанный СТЕК номер договора' not in ld_to_excel:
		ld_to_excel['Распознанный СТЕК номер договора']=[pay.recognized['agreement_by_inn']]
	else:
		ld_to_excel['Распознанный СТЕК номер договора'].append(pay.recognized['agreement_by_inn'])
	if 'Распознанный СТЕК название договора' not in ld_to_excel:
		ld_to_excel['Распознанный СТЕК название договора']=[pay.recognized['agreement_name_by_inn']]
	else:
		ld_to_excel['Распознанный СТЕК название договора'].append(pay.recognized['agreement_name_by_inn'])
	print()

# for key in ld_to_excel:
# 	print(key)


df = pd.DataFrame(ld_to_excel)
lc_excel_output_file_name = f'{sys.argv[1]}.xlsx'
echo(style(text=lc_excel_output_file_name, bg='blue', fg='bright_red'))
df.to_excel(lc_excel_output_file_name, engine='xlsxwriter')

lc_txt_output_file_name = f'{sys.argv[1]} - обработанный'
payroll.Save_strings_to_file(lc_txt_output_file_name)
echo(style(text=lc_txt_output_file_name, bg='blue', fg='bright_red'))


print()
echo(style(text=f"Замена получателя платежа: ", fg='green') + style(text=f"{ln_counter_changed}", fg='bright_green') + \
	style(text=f"\nНераспознанно: ", fg='red') + style(text=f"{ln_counter_unrecognized}", fg='bright_red') + \
		style(text=f"  из ", fg='yellow') + style(text=f"{len(payroll.pays)}", fg='bright_yellow'))
print()
print()
echo(style(text='Обработка файлов завершена', bg='bright_white', fg='green'))

time.sleep(10)

#df = pd.DataFrame({'Name': ['Manchester City', 'Real Madrid', 'Liverpool',
#                            'FC Bayern München', 'FC Barcelona', 'Juventus'],
#                   'League': ['English Premier League (1)', 'Spain Primera Division (1)',
#                              'English Premier League (1)', 'German 1. Bundesliga (1)',
#                              'Spain Primera Division (1)', 'Italian Serie A (1)'],
#                   'TransferBudget': [176000000, 188500000, 90000000,
#                                      100000000, 180500000, 105000000]})
#df.to_excel('teams.xlsx')

#print(ds.prefixes)
#print(payroll.list_of_pays)
	