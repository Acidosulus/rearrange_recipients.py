import sqlalchemy
import urllib
import pyodbc
from click import echo, style
import configparser  # импортируем библиотеку




def Get_list_of_agreements_details() -> list:
	config = configparser.ConfigParser()
	config.read("settings.ini", encoding='UTF-8')
	params = urllib.parse.quote_plus(f"DRIVER={config['login']['DRIVER']};"
	                                 f"SERVER={config['login']['SERVER']};"
	                                 f"DATABASE={config['login']['DATABASE']};"
	                                 f"UID={config['login']['UID']};"
	                                 f"PWD={config['login']['PWD']}")
	engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
	con = engine.connect()

	lc_sql_text = """			
				select distinct agreement_number, inn,kpp,agreement_name
				from (
				select		stack.[Договор].row_id as agreement_row_id,
							stack.[Договор].Номер as agreement_number,
							stack.[Организации].Название as agreement_name,
							stack.[Организации].Адрес as agreement_adres,
							stack.[Организации].ФактАдрес as agreement_adresfact,
							stack.[Организации].Телефон as agreement_phone,
							stack.[Организации].ИНН as inn, 
							stack.[Организации].КПП as kpp, 
							stack.[Организации].ОГРН as ogrn, 
							stack.[Организации].email as email, 
							stack.[Лицевые счета].row_id as point_id, 
							stack.[Лицевые счета].Номер as num_point, 
							stack.[Лицевые счета].Примечание as name_point, 
							stack.[Лицевые счета].АдресЛС as adres_point,
							staff1.ФИО as fio1,
							staff2.ФИО as fio2,
							staff3.ФИО as fio3,
							staff4.ФИО as fio4,
							stack.[Категории договоров].Код as kod_category,
							stack.[Категории договоров].Название as category,
							class01.Код as kod_clas,
							class01.Название as clas,
							class02.Код as kod_vid,
							class02.Название as vid,
							org_vid = 	CASE 
												when stack.[Организации].[Бюджет] = 1 then 'Бюджет'
												when stack.[Организации].[Бюджет] = 2 then 'Малый бизнес'
												when stack.[Организации].[Бюджет] = 3 then 'Средний бизнес'
												when stack.[Организации].[Бюджет] = 4 then 'Крупный бизнес'
												when stack.[Организации].[Бюджет] = 5 then 'Микропредприятия'
												else ''
											END
				from 	stack.[Лицевые договора],
						stack.[Лицевые счета], 
						stack.[Организации], 
						stack.[Договор]
				left join stack.[Сотрудники] as staff1 on staff1.ROW_ID = stack.[Договор].Сотрудник1
				left join stack.[Сотрудники] as staff2 on staff2.ROW_ID = stack.[Договор].Сотрудник2
				left join stack.[Сотрудники] as staff3 on staff3.ROW_ID = stack.[Договор].Сотрудник3
				left join stack.[Сотрудники] as staff4 on staff4.ROW_ID = stack.[Договор].Сотрудник4
				left join stack.[Категории договоров] on stack.[Категории договоров].ROW_ID = stack.[Договор].[Категория-Договоры] 
				left join stack.[Классификаторы] as class01 on class01.ROW_ID = stack.[Договор].[Отрасль-Договоры]
				left join stack.[Классификаторы] as class02 on class02.ROW_ID = stack.[Договор].[СправочникВД-Договоры]
				where 
						stack.[Договор].ROW_ID  = stack.[Лицевые договора].Договор and
						stack.[Лицевые счета].row_id = stack.[Лицевые договора].Лицевой and
						stack.[Организации].ROW_ID = stack.[Договор].Грузополучатель	 and 
						GETDATE()  between stack.[Лицевые договора].ДатНач and stack.[Лицевые договора].ДатКнц) as ct;"""
	result = engine.execute(lc_sql_text)
	agr_list = []
	for row in result:
		agr_list.append([row[0],row[1],row[2],row[3]])
	result.close()
	return agr_list

#print(Get_list_of_agreements_details())