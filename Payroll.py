from click import echo, style
import configparser  # импортируем библиотеку

def sx(source_string='', left_split='', right_split='', index=1) -> str:
	if source_string.count(
			left_split) < index:
		return ""
	lc_str = source_string
	for i in range(0, index):
		lc_str = lc_str[lc_str.find(left_split) + len(left_split):len(lc_str)]
	return lc_str[0:lc_str.find(right_split)]

def sxosl(source_list:list, left_split:str, right_split:str, index=1, include_ends=False) -> list:
	ln_skip_counter=index
	ll_result = []
	lb_start_copy = False
	for st in source_list:
		if left_split==st:
			#print(st, ln_skip_counter, lb_start_copy)
			if ln_skip_counter==1:
				lb_start_copy = True
				#print(st,'============================',lb_start_copy)
			else:
				ln_skip_counter += -1
		#print(lb_start_copy)
		if lb_start_copy==True:
			ll_result.append(st)
			#print(ll_result)
		
		if lb_start_copy and right_split==st:
			break
	#print(ll_result)
	#print(f'include_ends==False | {include_ends==False}')
	#print(f'len(ll_result)>=2 | {len(ll_result)>=2}')
	if include_ends==False and len(ll_result)>=2:
		ll_result = ll_result[1:len(ll_result)-1]
	return ll_result

class class_Payroll:
	def __init__(self, path_to_file:str) -> None:
		self.path_to_source_file = path_to_file
		self.Load_strings_from_file(self.path_to_source_file)


	def Load_strings_from_file(self, path_to_file) -> None:
		file = open(path_to_file, "r", encoding='cp1251')
		self.source_strings= file.readlines()
		file.close
		for i in range(len(self.source_strings)):
			self.source_strings[i] = self.source_strings[i].replace('\n','')


	def Save_strings_to_file(self, path_to_file:str) -> None:
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding='UTF-8')
		pn_files_count = int(config['unload']['SLICESCOUNT'])
		ll_files = []
		for i in range(pn_files_count):ll_files.append(open(f'{path_to_file} - 0{i+1}.txt', "w", encoding='cp1251'))
		for i in range(pn_files_count):ll_files[i].write('\n'.join(self.file_header)+'\n')
		counter = 0
		for pay in self.pays:
			counter += 1
			ll = pay.change_inn_kpp()
			ll_files[counter % pn_files_count].write('\n'.join(ll)+'\n')
		for i in range(pn_files_count):
			ll_files[i].write('КонецФайла\n')
			ll_files[i].close()


	def Parse_Strings_from_File(self) -> None:
		self.file_header = []
		#print(self.source_strings)
		self.file_header = sxosl(self.source_strings,'1CClientBankExchange','КонецРасчСчет',1,True)
		#print(type(self.source_strings), len(self.source_strings))
		#print(self.file_header)
		self.list_of_pays = []
		for i in range(self.source_strings.count('СекцияДокумент=Банковский ордер')):
			section = sxosl(self.source_strings,'СекцияДокумент=Банковский ордер','КонецДокумента',i+1,True)
			self.list_of_pays.append(section)
			#print(section)
		for i in range(self.source_strings.count('СекцияДокумент=Платежное поручение')):
			section = sxosl(self.source_strings,'СекцияДокумент=Платежное поручение','КонецДокумента',i+1,True)
			self.list_of_pays.append(section)
			#print(section)
		self.pays=[]
		for ll in self.list_of_pays:
			self.pays.append(Pay(ll))


class Pay():
	def __init__(self, source_list:list) -> None:
		self.source = source_list
		self.inn=''
		self.kpp=''
		self.purpose=''
		self.recognized={}
		for st in self.source:
			if 'ПлательщикИНН=' in st:
				self.inn = st[len('ПлательщикИНН='):len(st)]
			if 'ПлательщикКПП=' in st:
				self.kpp = st[len('ПлательщикКПП='):len(st)]
			if 'НазначениеПлатежа=' in st:
				self.purpose = st[len('НазначениеПлатежа='):len(st)]
		#print(f'{self.inn}    {self.kpp}   {self.purpose}')

	def change_inn_kpp(self) -> None:
		ll = self.source
		output_message = ''
		inn_change_flag = False
		if 'ПлательщикИНН=4633017746' in ll: # для самих себя не меняем ИНН/КПП
			return ll
		for i in range(len(ll)):
			if len(self.recognized['inn'])>0 and 'ПлательщикИНН=' in ll[i] and (self.recognized['inn'] not in ll[i]):
				ll[i]=f"ПлательщикИНН={self.recognized['inn']}"
				inn_change_flag=True
				output_message = style(text=f"замена ИНН с ", fg='yellow')+style(text=f"{self.inn}", fg='bright_yellow')+style(text=" на ",fg='yellow')+style(f"{self.recognized['inn']}", fg='bright_yellow')
		if inn_change_flag:
			for i in range(len(ll)):
				if len(self.recognized['inn'])>0 and 'ПлательщикКПП=' in ll[i] and self.kpp!=self.recognized['kpp'] and not(self.kpp=='0' and len(self.recognized['kpp'])==0):
					ll[i]=f"ПлательщикКПП={self.recognized['kpp']}"
					output_message += ' ' + style(text=f"замена КПП с ", fg='green')+style(text=f"{self.kpp}", fg='bright_green')+style(text=" на ",fg='green')+style(f"{self.recognized['kpp']}", fg='bright_green')
		if len(output_message)>0:
			echo(output_message+'  '+style(text=self.recognized['comment'], fg='bright_cyan'))
		return ll


#payroll = class_Payroll('.\\Октябрь\\31.10.2022\\31.10.2022_2290.txt')
#payroll.Load_strings_from_file(payroll.path_to_source_file)
#payroll.Parse_Strings_from_File()
#print(payroll.list_of_pays)
	