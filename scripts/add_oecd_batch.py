import json
d=json.load(open('indicators.json'))
F={'cofog':"OECD.GOV.GIP,DSD_GOV_COFOG@DF_GOV_COFOG_YU,1.0",'pf':"OECD.GOV.GIP,DSD_GOV@DF_GOV_PF_YU,1.0",'emp':"OECD.GOV.GIP,DSD_GOV@DF_GOV_EMPPS_REP_YU,1.0",
'house':"OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0",'wg':"OECD.ELS.SAE,DSD_EARNINGS@GENDER_WAGE_GAP,1.1",'ptg':"OECD.ELS.SAE,DSD_FTPT@DF_FTPT_INC_GEN,1.0",'temp':"OECD.ELS.SAE,DSD_TEMP@DF_TEMP_I_GEN,1.0",
'cls':"OECD.EDU.IMEP,DSD_EAG_UOE_NON_FIN_PERS@DF_UOE_NF_PERS_CLS,1.1",'enrl':"OECD.EDU.IMEP,DSD_EAG_UOE_NON_FIN_STUD@DF_UOE_NF_ENRL_RATE,1.1",'unemp':"OECD.EDU.IMEP,DSD_EAG_LSO_EA@DF_LSO_NEAC_UNEMP,1.0",'neet':"OECD.EDU.IMEP,DSD_EAG_LSO_EA@DF_LSO_TRANS,1.0",'earn':"OECD.EDU.IMEP,DSD_EAG_LSO_EA@DF_LSO_EARN_REL_UPPER,1.0",'attain':"OECD.EDU.IMEP,DSD_EAG_LSO_EA@DF_LSO_NEAC_DISTR_EA,1.0",
'tob':"OECD.ELS.HD,DSD_HEALTH_LVNG@DF_HEALTH_LVNG_TC,1.0",'util':"OECD.ELS.HD,DSD_HEALTH_PROC@DF_KEY_INDIC,1.2",'cover':"OECD.ELS.HD,DSD_HEALTH_PROT@DF_HEALTH_PROT,1.1",'ltc':"OECD.ELS.HD,DSD_HEALTH_LTCR@DF_HEALTH_LTCR,1.0",
'tw':"OECD.CTP.TPS,DSD_TAX_WAGES_DECOMP@DF_TW_DECOMP,2.1",'pit':"OECD.CTP.TPS,DSD_TAX_PIT@DF_PIT_AV_COMB,1.0",'cit':"OECD.CTP.TPS,DSD_TAX_CIT@DF_CIT,2.0",'fdi':"OECD.DAF.INV,DSD_FDI@DF_FDI_AGGR_SUMM,1.0",'tour':"OECD.CFE.TOU,DSD_TOURISM_KEY@DF_KEY_IND_PC,1.0",'eps':"OECD.ECO.MAD,DSD_EPS@DF_EPS,1.0",'gdpx':"OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HCPC,2.0",'hh':"OECD.SDD.NAD,DSD_NAAG@DF_NAAG_V,1.0"}
def cof(code,id_,name):
    return ("fiscal",id_,name,"% GDP","linear",F['cofog'],{"MEASURE":"GE","UNIT_MEASURE":"PT_B1GQ","EXPENDITURE":code})
rows=[
cof("GF01","cofog_gps","일반행정 지출 (정부기능별, GDP 대비)"),cof("GF03","cofog_order","공공질서·안전 지출 (정부기능별, GDP 대비)"),cof("GF04","cofog_econ","경제활동 지출 (정부기능별, GDP 대비)"),cof("GF05","cofog_env","환경보호 지출 (정부기능별, GDP 대비)"),cof("GF06","cofog_house","주택·지역사회 지출 (정부기능별, GDP 대비)"),cof("GF08","cofog_cult","문화·여가·종교 지출 (정부기능별, GDP 대비)"),
("fiscal","gov_bal","재정수지 (일반정부, GDP 대비)","% GDP","linear",F['pf'],{"MEASURE":"GNLB","UNIT_MEASURE":"PT_B1GQ"}),
("fiscal","gov_inv","정부 투자 (일반정부, GDP 대비)","% GDP","linear",F['pf'],{"MEASURE":"GINV","UNIT_MEASURE":"PT_B1GQ"}),
("fiscal","gov_int","이자지출 (일반정부, GDP 대비)","% GDP","linear",F['pf'],{"MEASURE":"GGINTN","UNIT_MEASURE":"PT_B1GQ"}),
("gov","gov_emp","공공부문 고용 비중 (총고용 대비)","%","linear",F['emp'],{"MEASURE":"EMPG","UNIT_MEASURE":"PT_EMP","SECTOR":"S13"}),
("gov","women_min","여성 장관 비율","%","linear",F['emp'],{"MEASURE":"EMPW_CMIN","UNIT_MEASURE":"PT_W"}),
("econ","hpi_real","실질 주택가격지수 (2015=100)","지수","linear",F['house'],{"MEASURE":"RHP","UNIT_MEASURE":"IX","FREQ":"A"}),
("econ","hpi_rent","주택가격 대비 임대료 지수 (2015=100)","지수","linear",F['house'],{"MEASURE":"HPI_RPI","UNIT_MEASURE":"IX","FREQ":"A"}),
("econ","hpi_inc","주택가격 대비 소득 지수 (2015=100)","지수","linear",F['house'],{"MEASURE":"HPI_YDH","UNIT_MEASURE":"IX","FREQ":"A"}),
("labour","wage_gap","성별 임금격차 (중위, 남성 대비)","%","linear",F['wg'],{"MEASURE":"GWP","UNIT_MEASURE":"PT_WG_SAL_M_D","AGGREGATION_OPERATION":"MEDIAN"}),
("labour","pt_f","시간제 근로 비중 (여성)","%","linear",F['ptg'],{"MEASURE":"EMP_PT","UNIT_MEASURE":"PT_POP_SUB","SEX":"F","AGE":"_T","WORKER_STATUS":"_T","METHODOLOGY":"OECD_DEF"}),
("labour","pt_m","시간제 근로 비중 (남성)","%","linear",F['ptg'],{"MEASURE":"EMP_PT","UNIT_MEASURE":"PT_POP_SUB","SEX":"M","AGE":"_T","WORKER_STATUS":"_T","METHODOLOGY":"OECD_DEF"}),
("labour","temp_emp","임시직 근로 비중","%","linear",F['temp'],{"MEASURE":"EMP_TEMP","UNIT_MEASURE":"PT_POP_SUB","AGE":"_T"}),
("edu","cls_prim","초등 학급당 학생 수","명","linear",F['cls'],{"MEASURE":"CLS","EDUCATION_LEV":"ISCED11_1","INST_TYPE_EDU":"INST_EDU"}),
("edu","cls_sec","중등(전기) 학급당 학생 수","명","linear",F['cls'],{"MEASURE":"CLS","EDUCATION_LEV":"ISCED11_2","INST_TYPE_EDU":"INST_EDU"}),
("edu","enrol3","3세 취학률","%","linear",F['enrl'],{"MEASURE":"ENRL","AGE":"Y3","SEX":"_T","EDUCATION_LEV":"_T","EDUCATION_TYPE":"FE"}),
("edu","enrol_1519","15~19세 취학률","%","linear",F['enrl'],{"MEASURE":"ENRL","AGE":"Y15T19","SEX":"_T","EDUCATION_LEV":"_T","EDUCATION_TYPE":"FE"}),
("edu","enrol_2024","20~24세 취학률","%","linear",F['enrl'],{"MEASURE":"ENRL","AGE":"Y20T24","SEX":"_T","EDUCATION_LEV":"_T","EDUCATION_TYPE":"FE"}),
("edu","neet","니트 비율 (15~29세)","%","linear",F['neet'],{"MEASURE":"POP","AGE":"Y15T29","SEX":"_T","ATTAINMENT_LEV":"_T","EDU_STATUS":"NED","LABOUR_FORCE_STATUS":"NE","STATISTICAL_OPERATION":"OBS"}),
("edu","unemp_low","실업률 (중졸 이하, 25~64세)","%","linear",F['unemp'],{"MEASURE":"UNEMPLOYMENT","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_0T2","STATISTICAL_OPERATION":"OBS"}),
("edu","unemp_mid","실업률 (고졸, 25~64세)","%","linear",F['unemp'],{"MEASURE":"UNEMPLOYMENT","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_3_4","STATISTICAL_OPERATION":"OBS"}),
("edu","unemp_high","실업률 (대졸 이상, 25~64세)","%","linear",F['unemp'],{"MEASURE":"UNEMPLOYMENT","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_5T8","STATISTICAL_OPERATION":"OBS"}),
("edu","attain_tert","대졸 이상 인구 비중 (25~64세)","%","linear",F['attain'],{"MEASURE":"POP","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_5T8","STATISTICAL_OPERATION":"OBS"}),
("edu","attain_low","중졸 이하 인구 비중 (25~64세)","%","linear",F['attain'],{"MEASURE":"POP","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_0T2","STATISTICAL_OPERATION":"OBS"}),
("edu","earn_tert","대졸 상대임금 (고졸=100, 25~64세)","지수","linear",F['earn'],{"MEASURE":"EARN_RELATIVE","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_5T8","WORK_TIME_ARNGMNT":"FT"}),
("edu","earn_low","중졸 이하 상대임금 (고졸=100, 25~64세)","지수","linear",F['earn'],{"MEASURE":"EARN_RELATIVE","AGE":"Y25T64","SEX":"_T","ATTAINMENT_LEV":"ISCED11A_0T2","WORK_TIME_ARNGMNT":"FT"}),
("health","smoke","매일 흡연율 (15세 이상)","%","linear",F['tob'],{"MEASURE":"SP_DS","UNIT_MEASURE":"PT_POP","AGE":"Y_GE15","SEX":"_T"}),
("health","tobacco_pc","담배 소비량 (15세 이상 1인당)","g","linear",F['tob'],{"MEASURE":"TBC","UNIT_MEASURE":"G_PS","AGE":"Y_GE15","SEX":"_T"}),
("health","consult","의사 진료 횟수 (1인당)","회","linear",F['util'],{"MEASURE":"CONSULT","UNIT_MEASURE":"CN_PS","CONSULTATION_TYPE":"_T"}),
("health","los","평균 재원일수 (급성기 입원)","일","linear",F['util'],{"MEASURE":"STAY","UNIT_MEASURE":"D","CARE_TYPE":"SOM"}),
("health","discharge","퇴원 건수 (10만명당)","건","linear",F['util'],{"MEASURE":"DISCHARGE","UNIT_MEASURE":"DSC_10P5PS","CARE_TYPE":"SOM"}),
("health","hc_cover","공공 의료보장 적용률","%","linear",F['cover'],{"MEASURE":"HIC","UNIT_MEASURE":"PT_POP","INSURANCE_TYPE":"COVGCMED"}),
("health","ltc_recip","노인 장기요양 수급률 (65세 이상)","%","linear",F['ltc'],{"MEASURE":"LTCR","UNIT_MEASURE":"PT_POP_Y_GE65","AGE":"Y_GE65","SEX":"_T","MODE_PROVISION":"_T"}),
("health","ltc_work","장기요양 인력 (65세 이상 100명당)","명","linear",F['ltc'],{"MEASURE":"FTE_FLTE","UNIT_MEASURE":"10P2HB_Y_GE65","HEALTH_PROF":"CARE","WORKER_STATUS":"_T","SEX":"_T","ATTAINMENT_LEV":"_T","WORK_TIME_ARNGMNT":"_T"}),
("fiscal","tax_wedge","근로소득 조세격차 (독신·평균임금)","% 노동비용","linear",F['tw'],{"MEASURE":"AV_TW","UNIT_MEASURE":"PT_COS_LB","HOUSEHOLD_TYPE":"S_C0","INCOME_PRINCIPAL":"AW100","CIVIL_STATUS":"_Z"}),
("fiscal","tax_wedge_fam","근로소득 조세격차 (부부·자녀 2명)","% 노동비용","linear",F['tw'],{"MEASURE":"AV_TW","UNIT_MEASURE":"PT_COS_LB","HOUSEHOLD_TYPE":"C_C2","INCOME_PRINCIPAL":"AW100","CIVIL_STATUS":"M"}),
("fiscal","pit","개인소득세+근로자 사회보험료 (독신, 총임금 대비)","%","linear",F['pit'],{"MEASURE":"PIT_EESSC","UNIT_MEASURE":"PT_WG_EARN_G","HOUSEHOLD_TYPE":"S_C0","CIVIL_STATUS":"_Z","INCOME_SPOUSE":"_Z"}),
("fiscal","cit","법인세율 (통합 법정세율)","%","linear",F['cit'],{"MEASURE":"CIT","UNIT_MEASURE":"PT_INC_TAX","TARGETING":"ST","SECTOR":"S13"}),
("ext","fdi_in","대내 FDI 잔액 (GDP 대비)","% GDP","linear",F['fdi'],{"MEASURE":"LE_FA_F","UNIT_MEASURE":"PT_B1GQ","MEASURE_PRINCIPLE":"DI","FREQ":"A"}),
("ext","fdi_out","대외 FDI 잔액 (GDP 대비)","% GDP","linear",F['fdi'],{"MEASURE":"LE_FA_F","UNIT_MEASURE":"PT_B1GQ","MEASURE_PRINCIPLE":"DO","FREQ":"A"}),
("econ","tour_gdp","관광산업 부가가치 비중 (GDP 대비)","% GDP","linear",F['tour'],{"MEASURE":"GDP_SH","UNIT_MEASURE":"PT_B1GQ"}),
("econ","tour_emp","관광산업 고용 비중","%","linear",F['tour'],{"MEASURE":"EMP_SH","UNIT_MEASURE":"PT_EMP"}),
("env","eps","환경정책 강도 지수 (EPS, 0~6)","점","linear",F['eps'],{"MEASURE":"POL_STRINGENCY","CLIM_POL":"EPS","UNIT_MEASURE":"0_TO_6"}),
("env","eps_mkt","환경정책 강도 (시장기반, 0~6)","점","linear",F['eps'],{"MEASURE":"POL_STRINGENCY","CLIM_POL":"EPS_MKT","UNIT_MEASURE":"0_TO_6"}),
("env","eps_nmkt","환경정책 강도 (비시장기반, 0~6)","점","linear",F['eps'],{"MEASURE":"POL_STRINGENCY","CLIM_POL":"EPS_NMKT","UNIT_MEASURE":"0_TO_6"}),
("econ","aic_pc","1인당 실질 개인소비 (PPP)","US$","log",F['gdpx'],{"TRANSACTION":"P41_POP","SECTOR":"S14","EXPENDITURE":"_T","UNIT_MEASURE":"USD_PPP_PS"}),
("welfare","hh_save","가계 순저축률","%","linear",F['hh'],{"MEASURE":"B8NS1M","UNIT_MEASURE":"PT_B6N_S1M","SECTOR":"S1M"}),
("welfare","hh_inc_pc","가계 실질 가처분소득 (1인당, PPP)","US$","log",F['hh'],{"MEASURE":"B6N_R_PPP_P31S14","UNIT_MEASURE":"USD_PPP_PS"}),
]
cats={c['id']:c for c in d['categories']}
have={i['id'] for c in d['categories'] for i in c['indicators']}
for cid,id_,name,unit,scale,flow,fl in rows:
    assert id_ not in have,id_
    e={"id":id_,"name":name,"unit":unit,"scale":scale,"source":"OECD","flow":flow,"filters":fl,"status":"ready"}
    if fl.get("FREQ")=="A" and False: pass
    cats[cid]['indicators'].append(e)
d['categories']=[c for c in d['categories'] if c['id']!='probe']
json.dump(d,open('indicators.json','w'),ensure_ascii=False)
print(len(rows),sum(len(c['indicators']) for c in d['categories']))
json.dump({r[1]:{"cat":r[0]} for r in rows},open('/tmp/newids.json','w'))
