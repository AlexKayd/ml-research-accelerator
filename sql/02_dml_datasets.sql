BEGIN;

INSERT INTO public.datasets VALUES (1, 'uci', '162', 'Forest Fires', 'This is a difficult regression task, where the aim is to predict the burned area of forest fires, in the northeast region of Portugal, by using meteorological and other data (see details at: http://www.dsi.uminho.pt/~pcortez/forestfires).



In [Cortez and Morais, 2007], the output ''area'' was first transformed with a ln(x+1) function.



   Then, several Data Mining methods were applied. After fitting the models, the outputs were



   post-processed with the inverse of the ln(x+1) transform. Four different input setups were



   used. The experiments were conducted using a 10-fold (cross-validation) x 30 runs. Two



   regression metrics were measured: MAD and RMSE. A Gaussian support vector machine (SVM) fed



   with only 4 direct weather conditions (temp, RH, wind and rain) obtained the best MAD value:



   12.71 +- 0.01 (mean and confidence interval within 95% using a t-student distribution). The



   best RMSE was attained by the naive mean predictor. An analysis to the regression error curve



   (REC) shows that the SVM model predicts more examples within a lower admitted error. In effect,



   the SVM model predicts better small fires, which are the majority.', '{"Climate and Environment",Multivariate,Regression}', 'csv', 28.22, 'active', 'https://archive.ics.uci.edu/static/public/162/forest+fires.zip', 'https://archive.ics.uci.edu/dataset/162/forest+fires', '2024-01-11 00:00:00', '''+1'':54,80 ''/~pcortez/forestfires).'':38 ''0.01'':134 ''10'':94 ''12.71'':133 ''2007'':43 ''30'':100 ''4'':119 ''95'':140 ''admit'':176 ''aim'':11 ''analysi'':158 ''appli'':62 ''area'':17,46 ''attain'':151 ''best'':130,148 ''better'':184 ''burn'':16 ''condit'':122 ''conduct'':91 ''confid'':137 ''cortez'':40 ''cross'':97 ''cross-valid'':96 ''curv'':163 ''data'':32,58 ''detail'':34 ''differ'':83 ''difficult'':6 ''direct'':120 ''distribut'':146 ''effect'':179 ''error'':162,177 ''exampl'':172 ''experi'':89 ''fed'':116 ''fire'':2,20,186 ''first'':48 ''fit'':64 ''fold'':95 ''forest'':1,19 ''four'':82 ''function'':55 ''gaussian'':111 ''input'':84 ''interv'':138 ''invers'':75 ''ln'':52,78 ''lower'':175 ''machin'':114 ''mad'':107,131 ''major'':190 ''mean'':135,155 ''measur'':106 ''meteorolog'':29 ''method'':60 ''metric'':104 ''mine'':59 ''model'':66,169,182 ''morai'':42 ''naiv'':154 ''northeast'':23 ''obtain'':128 ''output'':45,68 ''portug'':26 ''post'':71 ''post-process'':70 ''predict'':14,170,183 ''predictor'':156 ''process'':72 ''rain'':127 ''rec'':164 ''region'':24 ''regress'':7,103,161 ''rh'':124 ''rmse'':109,149 ''run'':101 ''see'':33 ''setup'':85 ''sever'':57 ''show'':165 ''small'':185 ''student'':145 ''support'':112 ''svm'':115,168,181 ''t-student'':143 ''task'':8 ''temp'':123 ''transform'':49,81 ''two'':102 ''use'':28,87,92,141 ''valid'':98 ''valu'':132 ''vector'':113 ''weather'':121 ''wind'':125 ''within'':139,173 ''www.dsi.uminho.pt'':37 ''www.dsi.uminho.pt/~pcortez/forestfires).'':36 ''x'':53,79,99');
INSERT INTO public.datasets VALUES (2, 'uci', '186', 'Wine Quality', 'Two datasets are included, related to red and white vinho verde wine samples, from the north of Portugal. The goal is to model wine quality based on physicochemical tests (see [Cortez et al., 2009], http://www3.dsi.uminho.pt/pcortez/wine/).



The two datasets are related to red and white variants of the Portuguese "Vinho Verde" wine. For more details, consult: http://www.vinhoverde.pt/en/ or the reference [Cortez et al., 2009].  Due to privacy and logistic issues, only physicochemical (inputs) and sensory (the output) variables are available (e.g. there is no data about grape types, wine brand, wine selling price, etc.).



These datasets can be viewed as classification or regression tasks.  The classes are ordered and not balanced (e.g. there are many more normal wines than excellent or poor ones). Outlier detection algorithms could be used to detect the few excellent or poor wines. Also, we are not sure if all input variables are relevant. So it could be interesting to test feature selection methods.', '{Business,Multivariate,Classification,Regression}', 'csv', 343.69, 'active', 'https://archive.ics.uci.edu/static/public/186/wine+quality.zip', 'https://archive.ics.uci.edu/dataset/186/wine+quality', '2023-11-15 00:00:00', '''/en/'':62 ''/pcortez/wine/).'':39 ''2009'':36,69 ''al'':35,68 ''algorithm'':131 ''also'':143 ''avail'':85 ''balanc'':116 ''base'':28 ''brand'':95 ''class'':111 ''classif'':106 ''consult'':59 ''cortez'':33,66 ''could'':132,156 ''data'':90 ''dataset'':4,42,101 ''detail'':58 ''detect'':130,136 ''due'':70 ''e.g'':86,117 ''et'':34,67 ''etc'':99 ''excel'':125,139 ''featur'':161 ''goal'':22 ''grape'':92 ''includ'':6 ''input'':78,150 ''interest'':158 ''issu'':75 ''logist'':74 ''mani'':120 ''method'':163 ''model'':25 ''normal'':122 ''north'':18 ''one'':128 ''order'':113 ''outlier'':129 ''output'':82 ''physicochem'':30,77 ''poor'':127,141 ''portug'':20 ''portugues'':52 ''price'':98 ''privaci'':72 ''qualiti'':2,27 ''red'':9,46 ''refer'':65 ''regress'':108 ''relat'':7,44 ''relev'':153 ''sampl'':15 ''see'':32 ''select'':162 ''sell'':97 ''sensori'':80 ''sure'':147 ''task'':109 ''test'':31,160 ''two'':3,41 ''type'':93 ''use'':134 ''variabl'':83,151 ''variant'':49 ''verd'':13,54 ''view'':104 ''vinho'':12,53 ''white'':11,48 ''wine'':1,14,26,55,94,96,123,142 ''www.vinhoverde.pt'':61 ''www.vinhoverde.pt/en/'':60 ''www3.dsi.uminho.pt'':38 ''www3.dsi.uminho.pt/pcortez/wine/).'':37');
INSERT INTO public.datasets VALUES (3, 'uci', '225', 'ILPD (Indian Liver Patient Dataset)', 'Death by liver cirrhosis continues to increase, given the increase in alcohol consumption rates, chronic hepatitis infections, and obesity-related liver disease. Notwithstanding the high mortality of this disease, liver diseases do not affect all sub-populations equally. The early detection of pathology is a determinant of patient outcomes, yet female patients appear to be marginalized when it comes to early diagnosis of liver pathology. 

The dataset comprises 584 patient records collected from the NorthEast of Andhra Pradesh, India.

The prediction task is to determine whether a patient suffers from liver disease based on the information about several biochemical markers, including albumin and other enzymes required for metabolism.





This data set contains records of 416 patients diagnosed with liver disease and 167 patients without liver disease. This information is contained in the class label named ''Selector''.  There are 10 variables per patient: age, gender, total Bilirubin, direct Bilirubin, total proteins, albumin, A/G ratio, SGPT, SGOT and Alkphos. Of the 583 patient records, 441 are male, and 142 are female. 



The current dataset has been used to study 

- differences in patients across US and Indian patients that suffer from liver diseases.

- gender-based disparities in predicting liver disease, as previous studies have found that biochemical markers do not have the same effectiveness for male and female patients.', '{"Health and Medicine",Multivariate,Classification}', 'csv', 23.20, 'active', 'https://archive.ics.uci.edu/static/public/225/ilpd+indian+liver+patient+dataset.zip', 'https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset', '2023-11-03 00:00:00', '''10'':146 ''142'':174 ''167'':129 ''416'':122 ''441'':170 ''583'':167 ''584'':76 ''a/g'':159 ''across'':188 ''affect'':40 ''age'':150 ''albumin'':109,158 ''alcohol'':17 ''alkpho'':164 ''andhra'':84 ''appear'':60 ''base'':100,200 ''bilirubin'':153,155 ''biochem'':106,212 ''chronic'':20 ''cirrhosi'':9 ''class'':140 ''collect'':79 ''come'':66 ''compris'':75 ''consumpt'':18 ''contain'':119,137 ''continu'':10 ''current'':178 ''data'':117 ''dataset'':5,74,179 ''death'':6 ''detect'':48 ''determin'':53,92 ''diagnos'':124 ''diagnosi'':69 ''differ'':185 ''direct'':154 ''diseas'':28,35,37,99,127,133,197,205 ''dispar'':201 ''earli'':47,68 ''effect'':219 ''enzym'':112 ''equal'':45 ''femal'':58,176,223 ''found'':210 ''gender'':151,199 ''gender-bas'':198 ''given'':13 ''hepat'':21 ''high'':31 ''ilpd'':1 ''includ'':108 ''increas'':12,15 ''india'':86 ''indian'':2,191 ''infect'':22 ''inform'':103,135 ''label'':141 ''liver'':3,8,27,36,71,98,126,132,196,204 ''male'':172,221 ''margin'':63 ''marker'':107,213 ''metabol'':115 ''mortal'':32 ''name'':142 ''northeast'':82 ''notwithstand'':29 ''obes'':25 ''obesity-rel'':24 ''outcom'':56 ''patholog'':50,72 ''patient'':4,55,59,77,95,123,130,149,168,187,192,224 ''per'':148 ''popul'':44 ''pradesh'':85 ''predict'':88,203 ''previous'':207 ''protein'':157 ''rate'':19 ''ratio'':160 ''record'':78,120,169 ''relat'':26 ''requir'':113 ''selector'':143 ''set'':118 ''sever'':105 ''sgot'':162 ''sgpt'':161 ''studi'':184,208 ''sub'':43 ''sub-popul'':42 ''suffer'':96,194 ''task'':89 ''total'':152,156 ''us'':189 ''use'':182 ''variabl'':147 ''whether'':93 ''without'':131 ''yet'':57');
INSERT INTO public.datasets VALUES (4, 'uci', '275', 'Bike Sharing', 'This dataset contains the hourly and daily count of rental bikes between years 2011 and 2012 in Capital bikeshare system with the corresponding weather and seasonal information.



Bike sharing systems are new generation of traditional bike rentals where whole process from membership, rental and return back has become automatic. Through these systems, user is able to easily rent a bike from a particular position and return back at another position. Currently, there are about over 500 bike-sharing programs around the world which is composed of over 500 thousands bicycles. Today, there exists great interest in these systems due to their important role in traffic, environmental and health issues. 







Apart from interesting real world applications of bike sharing systems, the characteristics of data being generated by these systems make them attractive for the research. Opposed to other transport services such as bus or subway, the duration of travel, departure and arrival position is explicitly recorded in these systems. This feature turns bike sharing system into a virtual sensor network that can be used for sensing mobility in the city. Hence, it is expected that most of important events in the city could be detected via monitoring these data.', '{"Social Science",Multivariate,Regression}', 'csv', 1191.32, 'active', 'https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip', 'https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset', '2024-03-10 00:00:00', '''2011'':16 ''2012'':18 ''500'':78,91 ''abl'':57 ''anoth'':71 ''apart'':113 ''applic'':118 ''around'':83 ''arriv'':154 ''attract'':134 ''automat'':51 ''back'':48,69 ''becom'':50 ''bicycl'':93 ''bike'':1,13,30,38,62,80,120,165 ''bike-shar'':79 ''bikeshar'':21 ''bus'':145 ''capit'':20 ''characterist'':124 ''citi'':182,194 ''compos'':88 ''contain'':5 ''correspond'':25 ''could'':195 ''count'':10 ''current'':73 ''daili'':9 ''data'':126,201 ''dataset'':4 ''departur'':152 ''detect'':197 ''due'':102 ''durat'':149 ''easili'':59 ''environment'':109 ''event'':191 ''exist'':96 ''expect'':186 ''explicit'':157 ''featur'':163 ''generat'':35,128 ''great'':97 ''health'':111 ''henc'':183 ''hour'':7 ''import'':105,190 ''inform'':29 ''interest'':98,115 ''issu'':112 ''make'':132 ''membership'':44 ''mobil'':179 ''monitor'':199 ''network'':172 ''new'':34 ''oppos'':138 ''particular'':65 ''posit'':66,72,155 ''process'':42 ''program'':82 ''real'':116 ''record'':158 ''rent'':60 ''rental'':12,39,45 ''research'':137 ''return'':47,68 ''role'':106 ''season'':28 ''sens'':178 ''sensor'':171 ''servic'':142 ''share'':2,31,81,121,166 ''subway'':147 ''system'':22,32,54,101,122,131,161,167 ''thousand'':92 ''today'':94 ''tradit'':37 ''traffic'':108 ''transport'':141 ''travel'':151 ''turn'':164 ''use'':176 ''user'':55 ''via'':198 ''virtual'':170 ''weather'':26 ''whole'':41 ''world'':85,117 ''year'':15');
INSERT INTO public.datasets VALUES (5, 'uci', '292', 'Wholesale customers', 'The data set refers to clients of a wholesale distributor. It includes the annual spending in monetary units (m.u.) on diverse product categories', '{Business,Multivariate,Classification,Clustering}', 'csv', 14.67, 'active', 'https://archive.ics.uci.edu/static/public/292/wholesale+customers.zip', 'https://archive.ics.uci.edu/dataset/292/wholesale+customers', '2024-02-05 00:00:00', '''annual'':16 ''categori'':25 ''client'':8 ''custom'':2 ''data'':4 ''distributor'':12 ''divers'':23 ''includ'':14 ''m.u'':21 ''monetari'':19 ''product'':24 ''refer'':6 ''set'':5 ''spend'':17 ''unit'':20 ''wholesal'':1,11');
INSERT INTO public.datasets VALUES (11, 'uci', '367', 'Dota2 Games Results', 'Dota 2 is a popular computer game with two teams of 5 players. At the start of the game each player chooses a unique hero with different strengths and weaknesses.



Dota 2 is a popular computer game with two teams of 5 players. At the start of the game each player chooses a unique hero with different strengths and weaknesses. The dataset is reasonably sparse as only 10 of 113 possible heroes are chosen in a given game. All games were played in a space of 2 hours on the 13th of August, 2016



The data was collected using: https://gist.github.com/da-steve101/1a7ae319448db431715bd75391a66e1b', '{Games,Multivariate,Classification}', 'csv', 24275.55, 'active', 'https://archive.ics.uci.edu/static/public/367/dota2+games+results.zip', 'https://archive.ics.uci.edu/dataset/367/dota2+games+results', '2024-04-13 00:00:00', '''/da-steve101/1a7ae319448db431715bd75391a66e1b'':105 ''10'':71 ''113'':73 ''13th'':94 ''2'':5,35,90 ''2016'':97 ''5'':15,45 ''august'':96 ''choos'':25,55 ''chosen'':77 ''collect'':101 ''comput'':9,39 ''data'':99 ''dataset'':65 ''differ'':30,60 ''dota'':4,34 ''dota2'':1 ''game'':2,10,22,40,52,81,83 ''gist.github.com'':104 ''gist.github.com/da-steve101/1a7ae319448db431715bd75391a66e1b'':103 ''given'':80 ''hero'':28,58,75 ''hour'':91 ''play'':85 ''player'':16,24,46,54 ''popular'':8,38 ''possibl'':74 ''reason'':67 ''result'':3 ''space'':88 ''spars'':68 ''start'':19,49 ''strength'':31,61 ''team'':13,43 ''two'':12,42 ''uniqu'':27,57 ''use'':102 ''weak'':33,63');
INSERT INTO public.datasets VALUES (6, 'uci', '296', 'Diabetes 130-US Hospitals for Years 1999-2008', 'The dataset represents ten years (1999-2008) of clinical care at 130 US hospitals and integrated delivery networks. Each row concerns hospital records of patients diagnosed with diabetes, who underwent laboratory, medications, and stayed up to 14 days. The goal is to determine the early readmission of the patient within 30 days of discharge.

The problem is important for the following reasons. Despite high-quality evidence showing improved clinical outcomes for diabetic patients who receive various preventive and therapeutic interventions, many patients do not receive them. This can be partially attributed to arbitrary diabetes management in hospital environments, which fail to attend to glycemic control. Failure to provide proper diabetes care not only increases the managing costs for the hospitals (as the patients are readmitted) but also impacts the morbidity and mortality of the patients, who may face complications associated with diabetes.





The dataset represents ten years (1999-2008) of clinical care at 130 US hospitals and integrated delivery networks. It includes over 50 features representing patient and hospital outcomes. Information was extracted from the database for encounters that satisfied the following criteria.

(1)	It is an inpatient encounter (a hospital admission).

(2)	It is a diabetic encounter, that is, one during which any kind of diabetes was entered into the system as a diagnosis.

(3)	The length of stay was at least 1 day and at most 14 days.

(4)	Laboratory tests were performed during the encounter.

(5)	Medications were administered during the encounter.



The data contains such attributes as patient number, race, gender, age, admission type, time in hospital, medical specialty of admitting physician, number of lab tests performed, HbA1c test result, diagnosis, number of medications, diabetic medications, number of outpatient, inpatient, and emergency visits in the year before the hospitalization, etc.', '{"Health and Medicine",Multivariate,Classification,Clustering}', 'csv', 18712.82, 'active', 'https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip', 'https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008', '2024-09-24 00:00:00', '''-2008'':8,15,158 ''1'':193,233 ''130'':2,20,163 ''14'':45,238 ''1999'':7,14,157 ''2'':202 ''3'':225 ''30'':59 ''4'':240 ''5'':248 ''50'':173 ''administ'':251 ''admiss'':201,266 ''admit'':274 ''age'':265 ''also'':136 ''arbitrari'':102 ''associ'':149 ''attend'':111 ''attribut'':100,259 ''care'':18,120,161 ''clinic'':17,78,160 ''complic'':148 ''concern'':29 ''contain'':257 ''control'':114 ''cost'':126 ''criteria'':192 ''data'':256 ''databas'':185 ''dataset'':10,153 ''day'':46,60,234,239 ''deliveri'':25,168 ''despit'':71 ''determin'':51 ''diabet'':1,36,81,103,119,151,206,216,288 ''diagnos'':34 ''diagnosi'':224,284 ''discharg'':62 ''earli'':53 ''emerg'':295 ''encount'':187,198,207,247,254 ''enter'':218 ''environ'':107 ''etc'':303 ''evid'':75 ''extract'':182 ''face'':147 ''fail'':109 ''failur'':115 ''featur'':174 ''follow'':69,191 ''gender'':264 ''glycem'':113 ''goal'':48 ''hba1c'':281 ''high'':73 ''high-qual'':72 ''hospit'':4,22,30,106,129,165,178,200,270,302 ''impact'':137 ''import'':66 ''improv'':77 ''includ'':171 ''increas'':123 ''inform'':180 ''inpati'':197,293 ''integr'':24,167 ''intervent'':89 ''kind'':214 ''lab'':278 ''laboratori'':39,241 ''least'':232 ''length'':227 ''manag'':104,125 ''mani'':90 ''may'':146 ''medic'':40,249,271,287,289 ''morbid'':139 ''mortal'':141 ''network'':26,169 ''number'':262,276,285,290 ''one'':210 ''outcom'':79,179 ''outpati'':292 ''partial'':99 ''patient'':33,57,82,91,132,144,176,261 ''perform'':244,280 ''physician'':275 ''prevent'':86 ''problem'':64 ''proper'':118 ''provid'':117 ''qualiti'':74 ''race'':263 ''readmiss'':54 ''readmit'':134 ''reason'':70 ''receiv'':84,94 ''record'':31 ''repres'':11,154,175 ''result'':283 ''row'':28 ''satisfi'':189 ''show'':76 ''specialti'':272 ''stay'':42,229 ''system'':221 ''ten'':12,155 ''test'':242,279,282 ''therapeut'':88 ''time'':268 ''type'':267 ''underw'':38 ''us'':3,21,164 ''various'':85 ''visit'':296 ''within'':58 ''year'':6,13,156,299');
INSERT INTO public.datasets VALUES (7, 'uci', '300', 'Tennis Major Tournament Match Statistics', 'This is a collection of 8 files containing the match statistics for both women and men at the four major tennis tournaments of the year 2013. Each file has 42 columns and a minimum of 76 rows.



N/A', '{Other,Multivariate,Classification,Regression,Clustering}', 'csv', 82.13, 'active', 'https://archive.ics.uci.edu/static/public/300/tennis+major+tournament+match+statistics.zip', 'https://archive.ics.uci.edu/dataset/300/tennis+major+tournament+match+statistics', '2024-03-29 00:00:00', '''2013'':31 ''42'':35 ''76'':41 ''8'':11 ''collect'':9 ''column'':36 ''contain'':13 ''file'':12,33 ''four'':24 ''major'':2,25 ''match'':4,15 ''men'':21 ''minimum'':39 ''n/a'':43 ''row'':42 ''statist'':5,16 ''tenni'':1,26 ''tournament'':3,27 ''women'':19 ''year'':30');
INSERT INTO public.datasets VALUES (8, 'uci', '332', 'Online News Popularity', 'This dataset summarizes a heterogeneous set of features about articles published by Mashable in a period of two years. The goal is to predict the number of shares in social networks (popularity).



* The articles were published by Mashable (www.mashable.com) and their content as the rights to reproduce it belongs to them. Hence, this dataset does not share the original content but some statistics associated with it. The original content be publicly accessed and retrieved using the provided urls.



* Acquisition date: January 8, 2015



* The estimated relative performance values were estimated by the authors using a Random Forest classifier and a rolling windows as assessment method.  See their article for more details on how the relative performance values were set.', '{Business,Multivariate,Classification,Regression}', 'csv', 23753.78, 'active', 'https://archive.ics.uci.edu/static/public/332/online+news+popularity.zip', 'https://archive.ics.uci.edu/dataset/332/online+news+popularity', '2024-02-15 00:00:00', '''2015'':86 ''8'':85 ''access'':75 ''acquisit'':82 ''articl'':13,37,111 ''assess'':107 ''associ'':67 ''author'':96 ''belong'':52 ''classifi'':101 ''content'':45,63,72 ''dataset'':5,57 ''date'':83 ''detail'':114 ''estim'':88,93 ''featur'':11 ''forest'':100 ''goal'':24 ''henc'':55 ''heterogen'':8 ''januari'':84 ''mashabl'':16,41 ''method'':108 ''network'':34 ''news'':2 ''number'':29 ''onlin'':1 ''origin'':62,71 ''perform'':90,119 ''period'':19 ''popular'':3,35 ''predict'':27 ''provid'':80 ''public'':74 ''publish'':14,39 ''random'':99 ''relat'':89,118 ''reproduc'':50 ''retriev'':77 ''right'':48 ''roll'':104 ''see'':109 ''set'':9,122 ''share'':31,60 ''social'':33 ''statist'':66 ''summar'':6 ''two'':21 ''url'':81 ''use'':78,97 ''valu'':91,120 ''window'':105 ''www.mashable.com'':42 ''year'':22');
INSERT INTO public.datasets VALUES (9, 'uci', '360', 'Air Quality', 'Contains the responses of a gas multisensor device deployed on the field in an Italian city. Hourly responses averages are recorded along with gas concentrations references from a certified analyzer. 



The dataset contains 9358 instances of hourly averaged responses from an array of 5 metal oxide chemical sensors embedded in an Air Quality Chemical Multisensor Device. The device was located on the field in a significantly polluted area, at road level,within an Italian city. Data were recorded from March 2004 to February 2005 (one year)representing the longest freely available recordings of on field deployed air quality chemical sensor devices responses. Ground Truth hourly averaged concentrations for CO, Non Metanic Hydrocarbons, Benzene, Total Nitrogen Oxides (NOx) and Nitrogen Dioxide (NO2)  and were provided by a co-located reference certified analyzer. Evidences of cross-sensitivities as well as both concept and sensor drifts are present as described in De Vito et al., Sens. And Act. B, Vol. 129,2,2008 (citation required) eventually affecting sensors concentration estimation capabilities. Missing values are tagged with -200 value.



This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded.', '{"Computer Science",Multivariate,Time-Series,Regression}', 'csv', 2034.44, 'active', 'https://archive.ics.uci.edu/static/public/360/air+quality.zip', 'https://archive.ics.uci.edu/dataset/360/air+quality', '2024-03-10 00:00:00', '''-200'':178 ''129'':162 ''2'':163 ''2004'':83 ''2005'':86 ''2008'':164 ''5'':46 ''9358'':36 ''act'':159 ''affect'':168 ''air'':1,54,99 ''al'':156 ''along'':24 ''analyz'':32,134 ''area'':70 ''array'':44 ''avail'':93 ''averag'':21,40,108 ''b'':160 ''benzen'':115 ''capabl'':172 ''certifi'':31,133 ''chemic'':49,56,101 ''citat'':165 ''citi'':18,77 ''co'':111,130 ''co-loc'':129 ''commerci'':189 ''concentr'':27,109,170 ''concept'':144 ''contain'':3,35 ''cross'':138 ''cross-sensit'':137 ''data'':78 ''dataset'':34,181 ''de'':153 ''deploy'':11,98 ''describ'':151 ''devic'':10,58,60,103 ''dioxid'':122 ''drift'':147 ''embed'':51 ''estim'':171 ''et'':155 ''eventu'':167 ''evid'':135 ''exclud'':193 ''exclus'':185 ''februari'':85 ''field'':14,65,97 ''freeli'':92 ''fulli'':192 ''gas'':8,26 ''ground'':105 ''hour'':19,39,107 ''hydrocarbon'':114 ''instanc'':37 ''italian'':17,76 ''level'':73 ''locat'':62,131 ''longest'':91 ''march'':82 ''metal'':47 ''metan'':113 ''miss'':173 ''multisensor'':9,57 ''nitrogen'':117,121 ''no2'':123 ''non'':112 ''nox'':119 ''one'':87 ''oxid'':48,118 ''pollut'':69 ''present'':149 ''provid'':126 ''purpos'':188,190 ''qualiti'':2,55,100 ''record'':23,80,94 ''refer'':28,132 ''repres'':89 ''requir'':166 ''research'':187 ''respons'':5,20,41,104 ''road'':72 ''sen'':157 ''sensit'':139 ''sensor'':50,102,146,169 ''signific'':68 ''tag'':176 ''total'':116 ''truth'':106 ''use'':184 ''valu'':174,179 ''vito'':154 ''vol'':161 ''well'':141 ''within'':74 ''year'':88');
INSERT INTO public.datasets VALUES (12, 'uci', '368', 'Facebook Metrics', 'Facebook performance metrics of a renowned cosmetic''s brand Facebook page.



The data is related to posts'' published during the year of 2014 on the Facebook''s page of a renowned cosmetics brand.



This dataset contains 500 of the 790 rows and part of the features analyzed by Moro et al. (2016). The remaining were omitted due to confidentiality issues.', '{Business,Multivariate,Regression}', 'csv', 38.58, 'active', 'https://archive.ics.uci.edu/static/public/368/facebook+metrics.zip', 'https://archive.ics.uci.edu/dataset/368/facebook+metrics', '2024-03-20 00:00:00', '''2014'':25 ''2016'':54 ''500'':39 ''790'':42 ''al'':53 ''analyz'':49 ''brand'':11,35 ''confidenti'':61 ''contain'':38 ''cosmet'':9,34 ''data'':15 ''dataset'':37 ''due'':59 ''et'':52 ''facebook'':1,3,12,28 ''featur'':48 ''issu'':62 ''metric'':2,5 ''moro'':51 ''omit'':58 ''page'':13,30 ''part'':45 ''perform'':4 ''post'':19 ''publish'':20 ''relat'':17 ''remain'':56 ''renown'':8,33 ''row'':43 ''year'':23');
INSERT INTO public.datasets VALUES (13, 'uci', '372', 'HTRU2', 'Pulsar candidates collected during the HTRU survey. Pulsars are a type of star, of considerable scientific interest. Candidates must be classified in to pulsar and non-pulsar classes to aid discovery.



HTRU2 is a data set which describes a sample of pulsar candidates collected during the High Time Resolution Universe Survey (South) [1]. 







Pulsars are a rare type of Neutron star that produce radio emission detectable here on Earth. They are of considerable scientific interest as probes of space-time, the inter-stellar medium, and states of matter (see [2] for more uses). 







As pulsars rotate, their emission beam sweeps across the sky, and when this crosses our line of sight, produces a detectable pattern of broadband radio emission. As pulsars



rotate rapidly, this pattern repeats periodically. Thus pulsar search involves looking for periodic radio signals with large radio telescopes.







Each pulsar produces a slightly different emission pattern, which varies slightly with each rotation (see [2] for an introduction to pulsar astrophysics to find out why). Thus a  potential signal detection known as a ''candidate'', is averaged over many rotations of the pulsar, as determined by the length of an observation. In the absence of additional info, each candidate could potentially describe a real pulsar. However in practice almost all detections are caused by radio frequency interference (RFI) and noise, making legitimate signals hard to find.







Machine learning tools are now being used to automatically label pulsar candidates to facilitate rapid analysis. Classification systems in particular are being widely adopted,



(see [4,5,6,7,8,9]) which treat the candidate data sets  as binary classification problems. Here the legitimate pulsar examples are a minority positive class, and spurious examples the majority negative class. At present multi-class labels are unavailable, given the costs associated with data annotation.







The data set shared here contains 16,259 spurious examples caused by RFI/noise, and 1,639 real pulsar examples. These examples have all been checked by human annotators. 







The data is presented in two formats: CSV and ARFF (used by the WEKA data mining tool). Candidates are stored in both files in separate rows. Each row lists the variables first, and the class label is the final entry. The class labels used are 0 (negative) and 1 (positive).







Please note that the data contains no positional information or other astronomical details. It is simply feature data extracted from candidate files using the PulsarFeatureLab tool (see [10]).', '{"Physics and Chemistry",Multivariate,Classification,Clustering}', 'csv', 3385.73, 'active', 'https://archive.ics.uci.edu/static/public/372/htru2.zip', 'https://archive.ics.uci.edu/dataset/372/htru2', '2024-04-03 00:00:00', '''0'':377 ''1'':55,318,380 ''10'':409 ''16'':310 ''2'':94,160 ''259'':311 ''4'':256 ''5'':257 ''6'':258 ''639'':319 ''7'':259 ''8'':260 ''9'':261 ''absenc'':198 ''across'':105 ''addit'':200 ''adopt'':254 ''aid'':32 ''almost'':213 ''analysi'':246 ''annot'':303,331 ''arff'':341 ''associ'':300 ''astronom'':393 ''astrophys'':166 ''automat'':239 ''averag'':181 ''beam'':103 ''binari'':269 ''broadband'':121 ''candid'':3,19,45,179,203,242,265,349,402 ''caus'':217,314 ''check'':328 ''class'':30,281,288,293,366,373 ''classif'':247,270 ''classifi'':22 ''collect'':4,46 ''consider'':16,75 ''contain'':309,387 ''cost'':299 ''could'':204 ''cross'':111 ''csv'':339 ''data'':37,266,302,305,333,346,386,399 ''describ'':40,206 ''detail'':394 ''detect'':68,118,175,215 ''determin'':189 ''differ'':150 ''discoveri'':33 ''earth'':71 ''emiss'':67,102,123,151 ''entri'':371 ''exampl'':276,284,313,322,324 ''extract'':400 ''facilit'':244 ''featur'':398 ''file'':354,403 ''final'':370 ''find'':168,230 ''first'':363 ''format'':338 ''frequenc'':220 ''given'':297 ''hard'':228 ''high'':49 ''howev'':210 ''htru'':7 ''htru2'':1,34 ''human'':330 ''info'':201 ''inform'':390 ''inter'':86 ''inter-stellar'':85 ''interest'':18,77 ''interfer'':221 ''introduct'':163 ''involv'':135 ''known'':176 ''label'':240,294,367,374 ''larg'':142 ''learn'':232 ''legitim'':226,274 ''length'':192 ''line'':113 ''list'':360 ''look'':136 ''machin'':231 ''major'':286 ''make'':225 ''mani'':183 ''matter'':92 ''medium'':88 ''mine'':347 ''minor'':279 ''multi'':292 ''multi-class'':291 ''must'':20 ''negat'':287,378 ''neutron'':62 ''nois'':224 ''non'':28 ''non-pulsar'':27 ''note'':383 ''observ'':195 ''particular'':250 ''pattern'':119,129,152 ''period'':131,138 ''pleas'':382 ''posit'':280,381,389 ''potenti'':173,205 ''practic'':212 ''present'':290,335 ''probe'':79 ''problem'':271 ''produc'':65,116,147 ''pulsar'':2,9,25,29,44,56,99,125,133,146,165,187,209,241,275,321 ''pulsarfeaturelab'':406 ''radio'':66,122,139,143,219 ''rapid'':127,245 ''rare'':59 ''real'':208,320 ''repeat'':130 ''resolut'':51 ''rfi'':222 ''rfi/noise'':316 ''rotat'':100,126,158,184 ''row'':357,359 ''sampl'':42 ''scientif'':17,76 ''search'':134 ''see'':93,159,255,408 ''separ'':356 ''set'':38,267,306 ''share'':307 ''sight'':115 ''signal'':140,174,227 ''simpli'':397 ''sky'':107 ''slight'':149,155 ''south'':54 ''space'':82 ''space-tim'':81 ''spurious'':283,312 ''star'':14,63 ''state'':90 ''stellar'':87 ''store'':351 ''survey'':8,53 ''sweep'':104 ''system'':248 ''telescop'':144 ''thus'':132,171 ''time'':50,83 ''tool'':233,348,407 ''treat'':263 ''two'':337 ''type'':12,60 ''unavail'':296 ''univers'':52 ''use'':97,237,342,375,404 ''vari'':154 ''variabl'':362 ''weka'':345 ''wide'':253');
INSERT INTO public.datasets VALUES (15, 'uci', '374', 'Appliances Energy Prediction', 'Experimental data used to create regression models of appliances energy use in a low energy building.



The data set is at 10 min for about 4.5 months. The house temperature and humidity conditions were monitored with a ZigBee wireless sensor network. Each wireless node transmitted the temperature and humidity conditions around 3.3 min. Then, the wireless data was averaged for 10 minutes periods. The energy data was logged every 10 minutes with m-bus energy meters. Weather from the nearest airport weather station (Chievres Airport, Belgium) was downloaded from a public data set from Reliable Prognosis (rp5.ru), and merged together with the experimental data sets using the date and time column. Two random variables have been included in the data set for testing the regression models and to filter out non predictive attributes (parameters).







For more information about the house, data collection, R scripts and figures, please refer to the paper and to the following github repository:







https://github.com/LuisM78/Appliances-energy-prediction-data', '{"Computer Science",Multivariate,Time-Series,Regression}', 'csv', 11698.60, 'active', 'https://archive.ics.uci.edu/static/public/374/appliances+energy+prediction.zip', 'https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction', '2024-03-29 00:00:00', '''/luism78/appliances-energy-prediction-data'':164 ''10'':25,64,73 ''3.3'':55 ''4.5'':29 ''airport'':85,89 ''applianc'':1,12 ''around'':54 ''attribut'':137 ''averag'':62 ''belgium'':90 ''build'':19 ''bus'':78 ''chievr'':88 ''collect'':146 ''column'':115 ''condit'':36,53 ''creat'':8 ''data'':5,21,60,69,96,108,124,145 ''date'':112 ''download'':92 ''energi'':2,13,18,68,79 ''everi'':72 ''experiment'':4,107 ''figur'':150 ''filter'':133 ''follow'':159 ''github'':160 ''github.com'':163 ''github.com/luism78/appliances-energy-prediction-data'':162 ''hous'':32,144 ''humid'':35,52 ''includ'':121 ''inform'':141 ''log'':71 ''low'':17 ''m'':77 ''m-bus'':76 ''merg'':103 ''meter'':80 ''min'':26,56 ''minut'':65,74 ''model'':10,130 ''monitor'':38 ''month'':30 ''nearest'':84 ''network'':44 ''node'':47 ''non'':135 ''paper'':155 ''paramet'':138 ''period'':66 ''pleas'':151 ''predict'':3,136 ''prognosi'':100 ''public'':95 ''r'':147 ''random'':117 ''refer'':152 ''regress'':9,129 ''reliabl'':99 ''repositori'':161 ''rp5.ru'':101 ''script'':148 ''sensor'':43 ''set'':22,97,109,125 ''station'':87 ''temperatur'':33,50 ''test'':127 ''time'':114 ''togeth'':104 ''transmit'':48 ''two'':116 ''use'':6,14,110 ''variabl'':118 ''weather'':81,86 ''wireless'':42,46,59 ''zigbe'':41');
INSERT INTO public.datasets VALUES (16, 'uci', '380', 'YouTube Spam Collection', 'It is a public set of comments collected for spam research. It has five datasets composed by 1,956 real messages extracted from five videos that were among the 10 most viewed on the collection period.



The table below lists the datasets, the YouTube video ID, the amount of samples in each class and the total number of samples per dataset.







Dataset --- YouTube ID -- # Spam - # Ham - Total



Psy ------- 9bZkp7q19f0 --- 175 --- 175 --- 350



KatyPerry - CevxZvSJLk8 --- 175 --- 175 --- 350



LMFAO ----- KQ6zr6kCPj8 --- 236 --- 202 --- 438



Eminem ---- uelHwf8o7_U --- 245 --- 203 --- 448



Shakira --- pRpeEdMmmQ0 --- 174 --- 196 --- 370







Note: the chronological order of the comments were kept.', '{"Computer Science",Text,Classification}', 'csv', 333.72, 'active', 'https://archive.ics.uci.edu/static/public/380/youtube+spam+collection.zip', 'https://archive.ics.uci.edu/dataset/380/youtube+spam+collection', '2024-04-03 00:00:00', '''1'':21 ''10'':33 ''174'':94 ''175'':73,74,78,79 ''196'':95 ''202'':84 ''203'':90 ''236'':83 ''245'':89 ''350'':75,80 ''370'':96 ''438'':85 ''448'':91 ''956'':22 ''9bzkp7q19f0'':72 ''among'':31 ''amount'':51 ''cevxzvsjlk8'':77 ''chronolog'':99 ''class'':56 ''collect'':3,11,38 ''comment'':10,103 ''compos'':19 ''dataset'':18,45,64,65 ''eminem'':86 ''extract'':25 ''five'':17,27 ''ham'':69 ''id'':49,67 ''katyperri'':76 ''kept'':105 ''kq6zr6kcpj8'':82 ''list'':43 ''lmfao'':81 ''messag'':24 ''note'':97 ''number'':60 ''order'':100 ''per'':63 ''period'':39 ''prpeedmmmq0'':93 ''psi'':71 ''public'':7 ''real'':23 ''research'':14 ''sampl'':53,62 ''set'':8 ''shakira'':92 ''spam'':2,13,68 ''tabl'':41 ''total'':59,70 ''u'':88 ''uelhwf8o7'':87 ''video'':28,48 ''view'':35 ''youtub'':1,47,66');
INSERT INTO public.datasets VALUES (17, 'uci', '381', 'Beijing PM2.5', 'This hourly data set contains the PM2.5 data of US Embassy in Beijing. Meanwhile, meteorological data from Beijing Capital International Airport are also included. 



The data''s time period is between Jan 1st, 2010 to Dec 31st, 2014. Missing data are denoted as "NA".', '{"Climate and Environment",Multivariate,Time-Series,Regression}', 'csv', 1963.37, 'active', 'https://archive.ics.uci.edu/static/public/381/beijing+pm2+5+data.zip', 'https://archive.ics.uci.edu/dataset/381/beijing+pm2+5+data', '2024-03-16 00:00:00', '''1st'':35 ''2010'':36 ''2014'':40 ''31st'':39 ''airport'':23 ''also'':25 ''beij'':1,15,20 ''capit'':21 ''contain'':7 ''data'':5,10,18,28,42 ''dec'':38 ''denot'':44 ''embassi'':13 ''hour'':4 ''includ'':26 ''intern'':22 ''jan'':34 ''meanwhil'':16 ''meteorolog'':17 ''miss'':41 ''na'':46 ''period'':31 ''pm2.5'':2,9 ''set'':6 ''time'':30 ''us'':12');
INSERT INTO public.datasets VALUES (80, 'kaggle', 'jasperan/league-of-legends-master-players', 'League of Legends Master+ Players', '# GitHub repository

[Click Here](https://github.com/oracle-devrel/leagueoflegends-optimizer)

# Why?

I am writing articles on League of Legends and Machine Learning. You can find the full repository where this information is stored [here](https://github.com/oracle-devrel/leagueoflegends-optimizer).
', '{games,categorical,tabular,json,python}', 'json', 44977.54, 'active', 'https://www.kaggle.com/api/v1/datasets/download/jasperan/league-of-legends-master-players', 'https://www.kaggle.com/datasets/jasperan/league-of-legends-master-players', '2021-09-22 01:39:39.093', '''/oracle-devrel/leagueoflegends-optimizer)'':12 ''/oracle-devrel/leagueoflegends-optimizer).'':39 ''articl'':17 ''click'':8 ''find'':27 ''full'':29 ''github'':6 ''github.com'':11,38 ''github.com/oracle-devrel/leagueoflegends-optimizer)'':10 ''github.com/oracle-devrel/leagueoflegends-optimizer).'':37 ''inform'':33 ''leagu'':1,19 ''learn'':24 ''legend'':3,21 ''machin'':23 ''master'':4 ''player'':5 ''repositori'':7,30 ''store'':35 ''write'':16');
INSERT INTO public.datasets VALUES (18, 'uci', '383', 'Cervical Cancer (Risk Factors)', 'This dataset focuses on the prediction of indicators/diagnosis of cervical cancer. The features cover demographic information, habits, and historic medical records.



The dataset was collected at ''Hospital Universitario de Caracas'' in Caracas, Venezuela. The dataset comprises demographic information, habits, and historic medical records of 858 patients. Several patients decided not to answer some of the questions because of privacy concerns (missing values).', '{"Health and Medicine",Multivariate,Classification}', 'csv', 99.67, 'active', 'https://archive.ics.uci.edu/static/public/383/cervical+cancer+risk+factors.zip', 'https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors', '2024-03-10 00:00:00', '''858'':49 ''answer'':56 ''cancer'':2,15 ''caraca'':34,36 ''cervic'':1,14 ''collect'':29 ''compris'':40 ''concern'':64 ''cover'':18 ''dataset'':6,27,39 ''de'':33 ''decid'':53 ''demograph'':19,41 ''factor'':4 ''featur'':17 ''focus'':7 ''habit'':21,43 ''histor'':23,45 ''hospit'':31 ''indicators/diagnosis'':12 ''inform'':20,42 ''medic'':24,46 ''miss'':65 ''patient'':50,52 ''predict'':10 ''privaci'':63 ''question'':60 ''record'':25,47 ''risk'':3 ''sever'':51 ''universitario'':32 ''valu'':66 ''venezuela'':37');
INSERT INTO public.datasets VALUES (19, 'uci', '396', 'Sales Transactions Weekly', 'Contains weekly purchased quantities of 800 over products over 52 weeks. Normalised values are provided too.



52 columns for 52 weeks; normalised values of provided too.', '{Business,Multivariate,Time-Series,Clustering}', 'csv', 309.96, 'active', 'https://archive.ics.uci.edu/static/public/396/sales+transactions+dataset+weekly.zip', 'https://archive.ics.uci.edu/dataset/396/sales+transactions+dataset+weekly', '2024-03-15 00:00:00', '''52'':13,20,23 ''800'':9 ''column'':21 ''contain'':4 ''normalis'':15,25 ''product'':11 ''provid'':18,28 ''purchas'':6 ''quantiti'':7 ''sale'':1 ''transact'':2 ''valu'':16,26 ''week'':3,5,14,24');
INSERT INTO public.datasets VALUES (20, 'uci', '409', 'Daily Demand Forecasting Orders', 'The dataset was collected during 60 days, this is a real database of a brazilian logistics company.



The database was collected during 60 days, this is a real database of a Brazilian company of large logistics. Twelve predictive attributes and a target that is the total of orders for daily. treatment', '{Business,Time-Series,Regression}', 'csv', 5.02, 'active', 'https://archive.ics.uci.edu/static/public/409/daily+demand+forecasting+orders.zip', 'https://archive.ics.uci.edu/dataset/409/daily+demand+forecasting+orders', '2024-03-21 00:00:00', '''60'':10,27 ''attribut'':43 ''brazilian'':19,36 ''collect'':8,25 ''compani'':21,37 ''daili'':1,54 ''databas'':16,23,33 ''dataset'':6 ''day'':11,28 ''demand'':2 ''forecast'':3 ''larg'':39 ''logist'':20,40 ''order'':4,52 ''predict'':42 ''real'':15,32 ''target'':46 ''total'':50 ''treatment'':55 ''twelv'':41');
INSERT INTO public.datasets VALUES (21, 'uci', '445', 'Absenteeism at work', 'The database was created with records of absenteeism at work from July 2007 to July 2010 at a courier company in Brazil.



The data set allows for several new combinations of attributes and attribute exclusions, or the modification of the attribute type (categorical, integer, or real) depending on the purpose of the research.The data set (Absenteeism at work - Part I) was used in academic research at the Universidade Nove de Julho - Postgraduate Program in Informatics and Knowledge Management.', '{Business,Multivariate,Time-Series,Classification,Clustering}', 'csv', 327.91, 'active', 'https://archive.ics.uci.edu/static/public/445/absenteeism+at+work.zip', 'https://archive.ics.uci.edu/dataset/445/absenteeism+at+work', '2024-03-08 00:00:00', '''2007'':16 ''2010'':19 ''absente'':1,11,59 ''academ'':67 ''allow'':29 ''attribut'':35,37,44 ''brazil'':25 ''categor'':46 ''combin'':33 ''compani'':23 ''courier'':22 ''creat'':7 ''data'':27,57 ''databas'':5 ''de'':73 ''depend'':50 ''exclus'':38 ''informat'':78 ''integ'':47 ''julho'':74 ''juli'':15,18 ''knowledg'':80 ''manag'':81 ''modif'':41 ''new'':32 ''nove'':72 ''part'':62 ''postgradu'':75 ''program'':76 ''purpos'':53 ''real'':49 ''record'':9 ''research'':68 ''research.the'':56 ''set'':28,58 ''sever'':31 ''type'':45 ''universidad'':71 ''use'':65 ''work'':3,13,61');
INSERT INTO public.datasets VALUES (22, 'uci', '451', 'Breast Cancer Coimbra', 'Clinical features were observed or measured for 64 patients with breast cancer and 52 healthy controls. 



There are 10 predictors, all quantitative, and a binary dependent variable, indicating the presence or absence of breast cancer. 



The predictors are anthropometric data and parameters which can be gathered in routine blood analysis. 



Prediction models based on these predictors, if accurate, can potentially be used as a biomarker of breast cancer.', '{"Health and Medicine",Multivariate,Classification}', 'csv', 25.41, 'active', 'https://archive.ics.uci.edu/static/public/451/breast+cancer+coimbra.zip', 'https://archive.ics.uci.edu/dataset/451/breast+cancer+coimbra', '2024-03-16 00:00:00', '''10'':22 ''52'':17 ''64'':11 ''absenc'':35 ''accur'':61 ''analysi'':53 ''anthropometr'':42 ''base'':56 ''binari'':28 ''biomark'':68 ''blood'':52 ''breast'':1,14,37,70 ''cancer'':2,15,38,71 ''clinic'':4 ''coimbra'':3 ''control'':19 ''data'':43 ''depend'':29 ''featur'':5 ''gather'':49 ''healthi'':18 ''indic'':31 ''measur'':9 ''model'':55 ''observ'':7 ''paramet'':45 ''patient'':12 ''potenti'':63 ''predict'':54 ''predictor'':23,40,59 ''presenc'':33 ''quantit'':25 ''routin'':51 ''use'':65 ''variabl'':30');
INSERT INTO public.datasets VALUES (44, 'uci', '601', 'AI4I 2020 Predictive Maintenance Dataset', 'The AI4I 2020 Predictive Maintenance Dataset is a synthetic dataset that reflects real predictive maintenance data encountered in industry.



Since real predictive maintenance datasets are generally difficult to obtain and in particular difficult to publish, we present and provide a synthetic dataset that reflects real predictive maintenance encountered in industry to the best of our knowledge.', '{"Computer Science",Multivariate,Time-Series,Classification,Regression,Causal-Discovery}', 'csv', 509.81, 'active', 'https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip', 'https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset', '2024-02-14 00:00:00', '''2020'':2,8 ''ai4i'':1,7 ''best'':58 ''data'':21 ''dataset'':5,11,15,29,47 ''difficult'':32,38 ''encount'':22,53 ''general'':31 ''industri'':24,55 ''knowledg'':61 ''mainten'':4,10,20,28,52 ''obtain'':34 ''particular'':37 ''predict'':3,9,19,27,51 ''present'':42 ''provid'':44 ''publish'':40 ''real'':18,26,50 ''reflect'':17,49 ''sinc'':25 ''synthet'':14,46');
INSERT INTO public.datasets VALUES (23, 'uci', '464', 'Superconductivty Data', 'Two file s contain data on 21263 superconductors and their relevant features.



There are two files: (1) train.csv contains 81 features extracted from 21263 superconductors along with the critical temperature in the 82nd column, (2) unique_m.csv contains the chemical formula broken up for all the 21263 superconductors from the train.csv file.  The last two columns have the critical temperature and chemical formula.  The original data comes from http://supercon.nims.go.jp/index_en.html which is public.  The goal here is to predict the critical temperature based on the features extracted.', '{"Physics and Chemistry",Multivariate,Regression}', 'csv', 27491.59, 'active', 'https://archive.ics.uci.edu/static/public/464/superconductivty+data.zip', 'https://archive.ics.uci.edu/dataset/464/superconductivty+data', '2024-03-29 00:00:00', '''/index_en.html'':72 ''1'':19 ''2'':37 ''21263'':9,26,48 ''81'':22 ''82nd'':35 ''along'':28 ''base'':85 ''broken'':43 ''chemic'':41,63 ''column'':36,57 ''come'':68 ''contain'':6,21,39 ''critic'':31,60,83 ''data'':2,7,67 ''extract'':24,89 ''featur'':14,23,88 ''file'':4,18,53 ''formula'':42,64 ''goal'':77 ''last'':55 ''origin'':66 ''predict'':81 ''public'':75 ''relev'':13 ''supercon.nims.go.jp'':71 ''supercon.nims.go.jp/index_en.html'':70 ''superconductivti'':1 ''superconductor'':10,27,49 ''temperatur'':32,61,84 ''train.csv'':20,52 ''two'':3,17,56 ''unique_m.csv'':38');
INSERT INTO public.datasets VALUES (24, 'uci', '468', 'Online Shoppers Purchasing Intention Dataset', 'Of the 12,330 sessions in the dataset,

84.5% (10,422) were negative class samples that did not

end with shopping, and the rest (1908) were positive class

samples ending with shopping.



The dataset consists of feature vectors belonging to 12,330 sessions. 



The dataset was formed so that each session



would belong to a different user in a 1-year period to avoid



any tendency to a specific campaign, special day, user



profile, or period.', '{Business,Multivariate,Classification,Clustering}', 'csv', 1046.94, 'active', 'https://archive.ics.uci.edu/static/public/468/online+shoppers+purchasing+intention+dataset.zip', 'https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset', '2024-01-11 00:00:00', '''1'':65 ''10'':15 ''12'':8,46 ''1908'':30 ''330'':9,47 ''422'':16 ''84.5'':14 ''avoid'':69 ''belong'':44,58 ''campaign'':75 ''class'':19,33 ''consist'':40 ''dataset'':5,13,39,50 ''day'':77 ''differ'':61 ''end'':24,35 ''featur'':42 ''form'':52 ''intent'':4 ''negat'':18 ''onlin'':1 ''period'':67,81 ''posit'':32 ''profil'':79 ''purchas'':3 ''rest'':29 ''sampl'':20,34 ''session'':10,48,56 ''shop'':26,37 ''shopper'':2 ''special'':76 ''specif'':74 ''tendenc'':71 ''user'':62,78 ''vector'':43 ''would'':57 ''year'':66');
INSERT INTO public.datasets VALUES (25, 'uci', '471', 'Electrical Grid Stability Simulated Data ', 'The local stability analysis of the 4-node star system (electricity producer is in the center) implementing Decentral Smart Grid Control concept. 



The analysis is performed for different sets of input values using the methodology similar to that described in [SchтФЬ╨УтФм╨┤fer, Benjamin, et al. ''Taming instabilities in power grid networks by decentralized control.'' The European Physical Journal Special Topics 225.3 (2016): 569-582.]. Several input values are kept the same: averaging time: 2 s; coupling strength: 8 s^-2; damping: 0.1 s^-1', '{"Physics and Chemistry",Multivariate,Classification,Regression}', 'csv', 2361.20, 'active', 'https://archive.ics.uci.edu/static/public/471/electrical+grid+stability+simulated+data.zip', 'https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data', '2024-01-09 00:00:00', '''-1'':90 ''-2'':86 ''-582'':70 ''0.1'':88 ''2'':80 ''2016'':68 ''225.3'':67 ''4'':12 ''569'':69 ''8'':84 ''al'':51 ''analysi'':9,29 ''averag'':78 ''benjamin'':49 ''center'':21 ''concept'':27 ''control'':26,60 ''coupl'':82 ''damp'':87 ''data'':5 ''decentr'':23,59 ''describ'':44 ''differ'':33 ''electr'':1,16 ''et'':50 ''european'':62 ''grid'':2,25,56 ''implement'':22 ''input'':36,72 ''instabl'':53 ''journal'':64 ''kept'':75 ''local'':7 ''methodolog'':40 ''network'':57 ''node'':13 ''perform'':31 ''physic'':63 ''power'':55 ''produc'':17 ''sch'':46 ''set'':34 ''sever'':71 ''similar'':41 ''simul'':4 ''smart'':24 ''special'':65 ''stabil'':3,8 ''star'':14 ''strength'':83 ''system'':15 ''tame'':52 ''time'':79 ''topic'':66 ''use'':38 ''valu'':37,73 ''╨│'':47 ''╨┤fer'':48');
INSERT INTO public.datasets VALUES (26, 'uci', '484', 'Travel Reviews', 'Reviews on destinations in 10 categories mentioned across East Asia. Each traveler rating is mapped as Excellent(4), Very Good(3), Average(2), Poor(1), and Terrible(0) and average rating is used.



This data set is populated by crawling TripAdvisor.com. Reviews on destinations in 10 categories mentioned across East Asia are considered. Each traveler rating is mapped as Excellent (4), Very Good (3), Average (2), Poor (1), and Terrible (0) and average rating is used against each category per user.', '{Other,Multivariate,Text,Classification,Clustering}', 'csv', 55.96, 'active', 'https://archive.ics.uci.edu/static/public/484/travel+reviews.zip', 'https://archive.ics.uci.edu/dataset/484/travel+reviews', '2024-03-15 00:00:00', '''0'':30,73 ''1'':27,70 ''10'':7,48 ''2'':25,68 ''3'':23,66 ''4'':20,63 ''across'':10,51 ''asia'':12,53 ''averag'':24,32,67,75 ''categori'':8,49,81 ''consid'':55 ''crawl'':42 ''data'':37 ''destin'':5,46 ''east'':11,52 ''excel'':19,62 ''good'':22,65 ''map'':17,60 ''mention'':9,50 ''per'':82 ''poor'':26,69 ''popul'':40 ''rate'':15,33,58,76 ''review'':2,3,44 ''set'':38 ''terribl'':29,72 ''travel'':1,14,57 ''tripadvisor.com'':43 ''use'':35,78 ''user'':83');
INSERT INTO public.datasets VALUES (27, 'uci', '485', 'Travel Review Ratings', 'Google reviews on attractions from 24 categories across Europe are considered. Google user rating ranges from 1 to 5 and average user rating per category is calculated.



This data set is populated by capturing user ratings from Google reviews. Reviews on attractions from 24 categories across Europe are considered. Google user rating ranges from 1 to 5 and average user rating per category is calculated.', '{Other,Multivariate,Text,Classification,Clustering}', 'csv', 622.07, 'active', 'https://archive.ics.uci.edu/static/public/485/tarvel+review+ratings.zip', 'https://archive.ics.uci.edu/dataset/485/tarvel+review+ratings', '2024-04-09 00:00:00', '''1'':20,58 ''24'':9,47 ''5'':22,60 ''across'':11,49 ''attract'':7,45 ''averag'':24,62 ''calcul'':30,68 ''captur'':37 ''categori'':10,28,48,66 ''consid'':14,52 ''data'':32 ''europ'':12,50 ''googl'':4,15,41,53 ''per'':27,65 ''popul'':35 ''rang'':18,56 ''rate'':3,17,26,39,55,64 ''review'':2,5,42,43 ''set'':33 ''travel'':1 ''user'':16,25,38,54,63');
INSERT INTO public.datasets VALUES (28, 'uci', '488', 'Facebook Live Sellers in Thailand', 'Facebook pages of 10 Thai fashion and cosmetics retail sellers. Posts of a different nature (video, photos, statuses, and links). Engagement metrics consist of comments, shares, and reactions.



The variability of consumer engagement is analysed through a Principal Component Analysis, highlighting the changes induced by the use of Facebook Live. The seasonal component is analysed through a study of the averages of the different engagement metrics for different time-frames (hourly, daily and monthly). Finally, we identify statistical outlier posts, that are qualitatively analyzed further, in terms of their selling approach and activities.', '{Business,Multivariate,Clustering}', 'csv', 357.77, 'active', 'https://archive.ics.uci.edu/static/public/488/facebook+live+sellers+in+thailand.zip', 'https://archive.ics.uci.edu/dataset/488/facebook+live+sellers+in+thailand', '2024-03-29 00:00:00', '''10'':9 ''activ'':99 ''analys'':40,60 ''analysi'':45 ''analyz'':90 ''approach'':97 ''averag'':66 ''chang'':48 ''comment'':30 ''compon'':44,58 ''consist'':28 ''consum'':37 ''cosmet'':13 ''daili'':78 ''differ'':19,69,73 ''engag'':26,38,70 ''facebook'':1,6,54 ''fashion'':11 ''final'':81 ''frame'':76 ''highlight'':46 ''hour'':77 ''identifi'':83 ''induc'':49 ''link'':25 ''live'':2,55 ''metric'':27,71 ''month'':80 ''natur'':20 ''outlier'':85 ''page'':7 ''photo'':22 ''post'':16,86 ''princip'':43 ''qualit'':89 ''reaction'':33 ''retail'':14 ''season'':57 ''sell'':96 ''seller'':3,15 ''share'':31 ''statist'':84 ''status'':23 ''studi'':63 ''term'':93 ''thai'':10 ''thailand'':5 ''time'':75 ''time-fram'':74 ''use'':52 ''variabl'':35 ''video'':21');
INSERT INTO public.datasets VALUES (29, 'uci', '503', 'Hepatitis C Virus (HCV) for Egyptian patients', 'Egyptian patients who underwent treatment dosages for HCV about 18 months. Discretization should be applied based on expert recommendations; there is an attached file shows how.', '{"Health and Medicine",Multivariate,Classification}', 'csv', 159.89, 'active', 'https://archive.ics.uci.edu/static/public/503/hepatitis+c+virus+hcv+for+egyptian+patients.zip', 'https://archive.ics.uci.edu/dataset/503/hepatitis+c+virus+hcv+for+egyptian+patients', '2024-04-09 00:00:00', '''18'':17 ''appli'':22 ''attach'':30 ''base'':23 ''c'':2 ''discret'':19 ''dosag'':13 ''egyptian'':6,8 ''expert'':25 ''file'':31 ''hcv'':4,15 ''hepat'':1 ''month'':18 ''patient'':7,9 ''recommend'':26 ''show'':32 ''treatment'':12 ''underw'':11 ''virus'':3');
INSERT INTO public.datasets VALUES (30, 'uci', '519', 'Heart Failure Clinical Records', 'This dataset contains the medical records of 299 patients who had heart failure, collected during their follow-up period, where each patient profile has 13 clinical features.



A detailed description of the dataset can be found in the Dataset section of the following paper: 







Davide Chicco, Giuseppe Jurman: "Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone". BMC Medical Informatics and Decision Making 20, 16 (2020). https://doi.org/10.1186/s12911-020-1023-5', '{"Health and Medicine",Multivariate,Classification,Regression,Clustering}', 'csv', 11.95, 'active', 'https://archive.ics.uci.edu/static/public/519/heart+failure+clinical+records.zip', 'https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records', '2024-02-26 00:00:00', '''/10.1186/s12911-020-1023-5'':82 ''13'':30 ''16'':78 ''20'':77 ''2020'':79 ''299'':12 ''alon'':70 ''bmc'':71 ''chicco'':51 ''clinic'':3,31 ''collect'':18 ''contain'':7 ''creatinin'':66 ''dataset'':6,38,44 ''david'':50 ''decis'':75 ''descript'':35 ''detail'':34 ''doi.org'':81 ''doi.org/10.1186/s12911-020-1023-5'':80 ''eject'':68 ''failur'':2,17,63 ''featur'':32 ''follow'':22,48 ''follow-up'':21 ''found'':41 ''fraction'':69 ''giusepp'':52 ''heart'':1,16,62 ''informat'':73 ''jurman'':53 ''learn'':55 ''machin'':54 ''make'':76 ''medic'':9,72 ''paper'':49 ''patient'':13,27,60 ''period'':24 ''predict'':57 ''profil'':28 ''record'':4,10 ''section'':45 ''serum'':65 ''surviv'':58');
INSERT INTO public.datasets VALUES (31, 'uci', '529', 'Early Stage Diabetes Risk Prediction', 'This dataset contains the sign and symptpom data of newly diabetic or would be diabetic patient. 



This has been col-



lected using direct questionnaires from the patients of Sylhet Diabetes



Hospital in Sylhet, Bangladesh and approved by a doctor.', '{"Computer Science",Multivariate,Classification}', 'csv', 33.87, 'active', 'https://archive.ics.uci.edu/static/public/529/early+stage+diabetes+risk+prediction+dataset.zip', 'https://archive.ics.uci.edu/dataset/529/early+stage+diabetes+risk+prediction+dataset', '2024-03-04 00:00:00', '''approv'':41 ''bangladesh'':39 ''col'':25 ''contain'':8 ''data'':13 ''dataset'':7 ''diabet'':3,16,20,35 ''direct'':28 ''doctor'':44 ''earli'':1 ''hospit'':36 ''lect'':26 ''newli'':15 ''patient'':21,32 ''predict'':5 ''questionnair'':29 ''risk'':4 ''sign'':10 ''stage'':2 ''sylhet'':34,38 ''symptpom'':12 ''use'':27 ''would'':18');
INSERT INTO public.datasets VALUES (32, 'uci', '536', 'Pedestrians in Traffic', 'This data-set contains a number of pedestrian tracks recorded from a vehicle driving in a town in southern Germany. The data is particularly well-suited for multi-agent motion prediction tasks.



The raw data was acquired from a vehicle equipped with multiple sensors while driving, for approximately five hours, in an urban area in southern Germany. The sensor set included one mono-RGB camera, one stereo-RGB camera, an inertial measurement system with differential GPS and a lidar system. The preprocessed data available from this repository consists of 45 pedestrian tracks (in world coordinates) together with a semantic map of the static environment. For each track and at each time-step, not only the agent position is provided, but also body and head orientation attributes, as well as the position of all other agents and their type (e.g. car, cyclist, pedestrian etc.). Additional details about the preprocessing pipeline can be found in [1]. More information on the data format is provided in the next section.', '{"Computer Science",Multivariate,Sequential,Time-Series,Classification,Regression,Causal-Discovery}', 'csv', 2210.01, 'active', 'https://archive.ics.uci.edu/static/public/536/pedestrian+in+traffic+dataset.zip', 'https://archive.ics.uci.edu/dataset/536/pedestrian+in+traffic+dataset', '2024-03-29 00:00:00', '''1'':163 ''45'':98 ''acquir'':43 ''addit'':153 ''agent'':35,125,144 ''also'':130 ''approxim'':54 ''area'':60 ''attribut'':135 ''avail'':92 ''bodi'':131 ''camera'':72,77 ''car'':149 ''consist'':96 ''contain'':8 ''coordin'':103 ''cyclist'':150 ''data'':6,26,41,91,168 ''data-set'':5 ''detail'':154 ''differenti'':83 ''drive'':18,52 ''e.g'':148 ''environ'':112 ''equip'':47 ''etc'':152 ''five'':55 ''format'':169 ''found'':161 ''germani'':24,63 ''gps'':84 ''head'':133 ''hour'':56 ''includ'':67 ''inerti'':79 ''inform'':165 ''lidar'':87 ''map'':108 ''measur'':80 ''mono'':70 ''mono-rgb'':69 ''motion'':36 ''multi'':34 ''multi-ag'':33 ''multipl'':49 ''next'':174 ''number'':10 ''one'':68,73 ''orient'':134 ''particular'':28 ''pedestrian'':1,12,99,151 ''pipelin'':158 ''posit'':126,140 ''predict'':37 ''preprocess'':90,157 ''provid'':128,171 ''raw'':40 ''record'':14 ''repositori'':95 ''rgb'':71,76 ''section'':175 ''semant'':107 ''sensor'':50,65 ''set'':7,66 ''southern'':23,62 ''static'':111 ''step'':121 ''stereo'':75 ''stereo-rgb'':74 ''suit'':31 ''system'':81,88 ''task'':38 ''time'':120 ''time-step'':119 ''togeth'':104 ''town'':21 ''track'':13,100,115 ''traffic'':3 ''type'':147 ''urban'':59 ''vehicl'':17,46 ''well'':30,137 ''well-suit'':29 ''world'':102');
INSERT INTO public.datasets VALUES (33, 'uci', '537', 'Cervical Cancer Behavior Risk', 'The dataset contains 19 attributes regarding ca cervix behavior risk with class label is ca_cervix with 1 and 0 as values which means the respondent with and without ca cervix, respectively.', '{"Health and Medicine",Multivariate,Univariate,Classification,Clustering}', 'csv', 4.01, 'active', 'https://archive.ics.uci.edu/static/public/537/cervical+cancer+behavior+risk.zip', 'https://archive.ics.uci.edu/dataset/537/cervical+cancer+behavior+risk', '2024-04-03 00:00:00', '''0'':24 ''1'':22 ''19'':8 ''attribut'':9 ''behavior'':3,13 ''ca'':11,19,34 ''cancer'':2 ''cervic'':1 ''cervix'':12,20,35 ''class'':16 ''contain'':7 ''dataset'':6 ''label'':17 ''mean'':28 ''regard'':10 ''respect'':36 ''respond'':30 ''risk'':4,14 ''valu'':26 ''without'':33');
INSERT INTO public.datasets VALUES (34, 'uci', '544', 'Estimation of Obesity Levels Based On Eating Habits and Physical Condition ', 'This dataset include data for the estimation of obesity levels in individuals from the countries of Mexico, Peru and Colombia, based on their eating habits and physical condition. 



This dataset include data for the estimation of obesity levels in individuals from the countries of Mexico, Peru and Colombia, based on their eating habits and physical condition. The data contains 17 attributes and 2111 records, the records are labeled with the class variable NObesity (Obesity Level), that allows classification of the data using the values of Insufficient Weight, Normal Weight, Overweight Level I, Overweight Level II, Obesity Type I, Obesity Type II and Obesity Type III. 77% of the data was generated synthetically using the Weka tool and the SMOTE filter, 23% of the data was collected directly from users through a web platform.', '{"Health and Medicine",Multivariate,Classification,Regression,Clustering}', 'csv', 257.47, 'active', 'https://archive.ics.uci.edu/static/public/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition.zip', 'https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition', '2024-09-10 00:00:00', '''17'':71 ''2111'':74 ''23'':132 ''77'':117 ''allow'':88 ''attribut'':72 ''base'':5,32,60 ''class'':82 ''classif'':89 ''collect'':137 ''colombia'':31,59 ''condit'':11,39,67 ''contain'':70 ''countri'':26,54 ''data'':15,43,69,92,120,135 ''dataset'':13,41 ''direct'':138 ''eat'':7,35,63 ''estim'':1,18,46 ''filter'':131 ''generat'':122 ''habit'':8,36,64 ''ii'':106,112 ''iii'':116 ''includ'':14,42 ''individu'':23,51 ''insuffici'':97 ''label'':79 ''level'':4,21,49,86,102,105 ''mexico'':28,56 ''nobes'':84 ''normal'':99 ''obes'':3,20,48,85,107,110,114 ''overweight'':101,104 ''peru'':29,57 ''physic'':10,38,66 ''platform'':144 ''record'':75,77 ''smote'':130 ''synthet'':123 ''tool'':127 ''type'':108,111,115 ''use'':93,124 ''user'':140 ''valu'':95 ''variabl'':83 ''web'':143 ''weight'':98,100 ''weka'':126');
INSERT INTO public.datasets VALUES (35, 'uci', '547', 'Algerian Forest Fires', 'The dataset includes 244 instances that regroup a data of two regions of Algeria.



The dataset includes 244 instances that regroup a data of two regions of Algeria,namely the Bejaia region located in the northeast of Algeria and the Sidi Bel-abbes region located in the northwest of Algeria.







122 instances for each region. 







The period from June 2012 to September 2012. 



The dataset includes 11 attribues and 1 output attribue (class)



The 244 instances have been classified into тФЬ╨▓╤В╨Т╨╝тХж╨мfireтФЬ╨▓╤В╨Т╨╝╤В╨Ф╨▓ (138 classes) and тФЬ╨▓╤В╨Т╨╝тХж╨мnot fireтФЬ╨▓╤В╨Т╨╝╤В╨Ф╨▓ (106 classes) classes.', '{Biology,Multivariate,Classification,Regression}', 'csv', 14.41, 'active', 'https://archive.ics.uci.edu/static/public/547/algerian+forest+fires+dataset.zip', 'https://archive.ics.uci.edu/dataset/547/algerian+forest+fires+dataset', '2024-03-19 00:00:00', '''1'':74 ''106'':95 ''11'':71 ''122'':55 ''138'':88 ''2012'':64,67 ''244'':7,21,79 ''abb'':47 ''algeria'':17,31,41,54 ''algerian'':1 ''attribu'':72,76 ''bejaia'':34 ''bel'':46 ''bel-abb'':45 ''class'':77,89,96,97 ''classifi'':83 ''data'':12,26 ''dataset'':5,19,69 ''fire'':3,93 ''forest'':2 ''includ'':6,20,70 ''instanc'':8,22,56,80 ''june'':63 ''locat'':36,49 ''name'':32 ''northeast'':39 ''northwest'':52 ''output'':75 ''period'':61 ''region'':15,29,35,48,59 ''regroup'':10,24 ''septemb'':66 ''sidi'':44 ''two'':14,28 ''╨▓╤В╨▓╨╝'':85,91 ''╨▓╤В╨▓╨╝╤В╨┤╨▓'':87,94 ''╤Мfire'':86 ''╤Мnot'':92');
INSERT INTO public.datasets VALUES (36, 'uci', '551', 'Gas Turbine CO and NOx Emission Data Set', 'The dataset contains 36733 instances of 11 sensor measures aggregated over one hour, from a gas turbine located in Turkey for the purpose of studying flue gas emissions, namely CO and NOx.



The dataset contains 36733 instances of 11 sensor measures aggregated over one hour (by means of average or sum) from a gas turbine located in Turkey''s north western region for the purpose of studying flue gas emissions, namely CO and NOx (NO + NO2). The data comes from the same power plant as the dataset (http://archive.ics.uci.edu/ml/datasets/Combined+Cycle+Power+Plant) used for predicting hourly net energy yield. By contrast, this data is collected in another data range (01.01.2011 - 31.12.2015), includes gas turbine parameters (such as Turbine Inlet Temperature and Compressor Discharge pressure) in addition to the ambient variables. Note that the dates are not given in the instances but the data are sorted in chronological order. See the attribute information and relevant paper for details. Kindly follow the protocol mentioned in the paper (using the first three years'' data for training/ cross-validation and the last two for testing) for reproducibility and comparability of works. The dataset can be well used for predicting turbine energy yield (TEY) using ambient variables as features.', '{"Computer Science",Multivariate,Regression,Clustering}', 'csv', 2713.69, 'active', 'https://archive.ics.uci.edu/static/public/551/gas+turbine+co+and+nox+emission+data+set.zip', 'https://archive.ics.uci.edu/dataset/551/gas+turbine+co+and+nox+emission+data+set', '2024-03-29 00:00:00', '''/ml/datasets/combined+cycle+power+plant)'':98 ''01.01.2011'':116 ''11'':15,47 ''31.12.2015'':117 ''36733'':12,44 ''addit'':132 ''aggreg'':18,50 ''ambient'':135,208 ''anoth'':113 ''archive.ics.uci.edu'':97 ''archive.ics.uci.edu/ml/datasets/combined+cycle+power+plant)'':96 ''attribut'':157 ''averag'':57 ''chronolog'':153 ''co'':3,38,80 ''collect'':111 ''come'':87 ''compar'':192 ''compressor'':128 ''contain'':11,43 ''contrast'':107 ''cross'':181 ''cross-valid'':180 ''data'':7,86,109,114,149,177 ''dataset'':10,42,95,196 ''date'':140 ''detail'':163 ''discharg'':129 ''emiss'':6,36,78 ''energi'':104,204 ''featur'':211 ''first'':174 ''flue'':34,76 ''follow'':165 ''gas'':1,24,35,62,77,119 ''given'':143 ''hour'':21,53,102 ''includ'':118 ''inform'':158 ''inlet'':125 ''instanc'':13,45,146 ''kind'':164 ''last'':185 ''locat'':26,64 ''mean'':55 ''measur'':17,49 ''mention'':168 ''name'':37,79 ''net'':103 ''no2'':84 ''north'':68 ''note'':137 ''nox'':5,40,82 ''one'':20,52 ''order'':154 ''paper'':161,171 ''paramet'':121 ''plant'':92 ''power'':91 ''predict'':101,202 ''pressur'':130 ''protocol'':167 ''purpos'':31,73 ''rang'':115 ''region'':70 ''relev'':160 ''reproduc'':190 ''see'':155 ''sensor'':16,48 ''set'':8 ''sort'':151 ''studi'':33,75 ''sum'':59 ''temperatur'':126 ''test'':188 ''tey'':206 ''three'':175 ''train'':179 ''turbin'':2,25,63,120,124,203 ''turkey'':28,66 ''two'':186 ''use'':99,172,200,207 ''valid'':182 ''variabl'':136,209 ''well'':199 ''western'':69 ''work'':194 ''year'':176 ''yield'':105,205');
INSERT INTO public.datasets VALUES (37, 'uci', '560', 'Seoul Bike Sharing Demand', 'The dataset contains count of public bicycles rented per hour in the Seoul Bike Sharing System, with corresponding weather data and holiday information



Currently Rental bikes are introduced in many urban cities for the enhancement of mobility comfort. It is important to make the rental bike available and accessible to the public at the right time as it lessens the waiting time. Eventually, providing the city with a stable supply of rental bikes becomes a major concern. The crucial part is the prediction of bike count required at each hour for the stable supply of rental bikes. 



The dataset contains weather information (Temperature, Humidity, Windspeed, Visibility, Dewpoint, Solar radiation, Snowfall, Rainfall), the number of bikes rented per hour and date information.', '{Business,Multivariate,Regression}', 'csv', 590.01, 'active', 'https://archive.ics.uci.edu/static/public/560/seoul+bike+sharing+demand.zip', 'https://archive.ics.uci.edu/dataset/560/seoul+bike+sharing+demand', '2024-02-05 00:00:00', '''access'':53 ''avail'':51 ''becom'':78 ''bicycl'':11 ''bike'':2,18,30,50,77,89,101,119 ''citi'':36,70 ''comfort'':42 ''concern'':81 ''contain'':7,104 ''correspond'':22 ''count'':8,90 ''crucial'':83 ''current'':28 ''data'':24 ''dataset'':6,103 ''date'':124 ''demand'':4 ''dewpoint'':111 ''enhanc'':39 ''eventu'':67 ''holiday'':26 ''hour'':14,94,122 ''humid'':108 ''import'':45 ''inform'':27,106,125 ''introduc'':32 ''lessen'':63 ''major'':80 ''make'':47 ''mani'':34 ''mobil'':41 ''number'':117 ''part'':84 ''per'':13,121 ''predict'':87 ''provid'':68 ''public'':10,56 ''radiat'':113 ''rainfal'':115 ''rent'':12,120 ''rental'':29,49,76,100 ''requir'':91 ''right'':59 ''seoul'':1,17 ''share'':3,19 ''snowfal'':114 ''solar'':112 ''stabl'':73,97 ''suppli'':74,98 ''system'':20 ''temperatur'':107 ''time'':60,66 ''urban'':35 ''visibl'':110 ''wait'':65 ''weather'':23,105 ''windspe'':109');
INSERT INTO public.datasets VALUES (52, 'uci', '759', 'Glioma Grading Clinical and Mutation Features', 'Gliomas are the most common primary tumors of the brain. They can be graded as LGG (Lower-Grade Glioma) or GBM (Glioblastoma Multiforme) depending on the histological/imaging criteria. Clinical and molecular/mutation factors are also very crucial for the grading process. Molecular tests are expensive to help accurately diagnose glioma patients.    In this dataset, the most frequently mutated 20 genes and 3 clinical features are considered from TCGA-LGG and TCGA-GBM brain glioma projects.  The prediction task is to determine whether a patient is LGG or GBM with a given clinical and molecular/mutation features. The main objective is to find the optimal subset of mutation genes and clinical features for the glioma grading process to improve performance and reduce costs.  ', '{"Health and Medicine",Tabular,Multivariate,Classification,Other}', 'csv', 301.52, 'active', 'https://archive.ics.uci.edu/static/public/759/glioma+grading+clinical+and+mutation+features+dataset.zip', 'https://archive.ics.uci.edu/dataset/759/glioma+grading+clinical+and+mutation+features+dataset', '2023-11-03 00:00:00', '''20'':65 ''3'':68 ''accur'':54 ''also'':41 ''brain'':16,81 ''clinic'':3,36,69,100,117 ''common'':11 ''consid'':72 ''cost'':129 ''criteria'':35 ''crucial'':43 ''dataset'':60 ''depend'':31 ''determin'':89 ''diagnos'':55 ''expens'':51 ''factor'':39 ''featur'':6,70,103,118 ''find'':109 ''frequent'':63 ''gbm'':28,80,96 ''gene'':66,115 ''given'':99 ''glioblastoma'':29 ''glioma'':1,7,26,56,82,121 ''grade'':2,20,25,46,122 ''help'':53 ''histological/imaging'':34 ''improv'':125 ''lgg'':22,76,94 ''lower'':24 ''lower-grad'':23 ''main'':105 ''molecular'':48 ''molecular/mutation'':38,102 ''multiform'':30 ''mutat'':5,64,114 ''object'':106 ''optim'':111 ''patient'':57,92 ''perform'':126 ''predict'':85 ''primari'':12 ''process'':47,123 ''project'':83 ''reduc'':128 ''subset'':112 ''task'':86 ''tcga'':75,79 ''tcga-gbm'':78 ''tcga-lgg'':74 ''test'':49 ''tumor'':13 ''whether'':90');
INSERT INTO public.datasets VALUES (38, 'uci', '563', 'Iranian Churn', 'This dataset is randomly collected from an Iranian telecom company''s database over a period of 12 months.



This dataset is randomly collected from an Iranian telecom companyтФЬ╨▓╤В╨Т╨╝╤В╨Ф╨▓s database over a period of 12 months. A total of 3150 rows of data, each representing a customer, bear information for 13 columns. The attributes that are in this dataset



are call failures, frequency of SMS, number of complaints, number of distinct calls, subscription length, age group, the charge amount, type of service, seconds of use, status, frequency of use, and Customer Value.







All of the attributes except for attribute churn is the aggregated data of the first 9 months. The churn labels are the state of the customers at the end of 12 months. The three months is the designated planning gap.', '{Business,Multivariate,Classification,Regression}', 'csv', 128.64, 'active', 'https://archive.ics.uci.edu/static/public/563/iranian+churn+dataset.zip', 'https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset', '2024-03-09 00:00:00', '''12'':19,37,125 ''13'':53 ''3150'':42 ''9'':110 ''age'':77 ''aggreg'':105 ''amount'':81 ''attribut'':56,98,101 ''bear'':50 ''call'':63,74 ''charg'':80 ''churn'':2,102,113 ''collect'':7,25 ''column'':54 ''compani'':12,30 ''complaint'':70 ''custom'':49,93,120 ''data'':45,106 ''databas'':14,32 ''dataset'':4,22,61 ''design'':132 ''distinct'':73 ''end'':123 ''except'':99 ''failur'':64 ''first'':109 ''frequenc'':65,89 ''gap'':134 ''group'':78 ''inform'':51 ''iranian'':1,10,28 ''label'':114 ''length'':76 ''month'':20,38,111,126,129 ''number'':68,71 ''period'':17,35 ''plan'':133 ''random'':6,24 ''repres'':47 ''row'':43 ''second'':85 ''servic'':84 ''sms'':67 ''state'':117 ''status'':88 ''subscript'':75 ''telecom'':11,29 ''three'':128 ''total'':40 ''type'':82 ''use'':87,91 ''valu'':94 ''╨▓╤В╨▓╨╝╤В╨┤╨▓s'':31');
INSERT INTO public.datasets VALUES (39, 'uci', '567', 'COVID-19 Surveillance', 'Coronavirus Disease (COVID-19) Surveillance.



Guidelines for Prevention and Control of Coronavirus Disease (COVID-19).', '{"Computer Science",Multivariate,Classification}', 'csv', 0.30, 'active', 'https://archive.ics.uci.edu/static/public/567/covid+19+surveillance.zip', 'https://archive.ics.uci.edu/dataset/567/covid+19+surveillance', '2024-04-09 00:00:00', '''-19'':2,7,18 ''control'':13 ''coronavirus'':4,15 ''covid'':1,6,17 ''diseas'':5,16 ''guidelin'':9 ''prevent'':11 ''surveil'':3,8');
INSERT INTO public.datasets VALUES (40, 'uci', '571', 'HCV data', 'The data set contains laboratory values of blood donors and Hepatitis C patients and demographic values like age.



The target attribute for classification is Category (blood donors vs. Hepatitis C, including its progress: ''just'' Hepatitis C, Fibrosis, Cirrhosis).', '{"Health and Medicine",Multivariate,Classification,Clustering}', 'csv', 45.10, 'active', 'https://archive.ics.uci.edu/static/public/571/hcv+data.zip', 'https://archive.ics.uci.edu/dataset/571/hcv+data', '2023-11-03 00:00:00', '''age'':20 ''attribut'':23 ''blood'':10,28 ''c'':14,32,38 ''categori'':27 ''cirrhosi'':40 ''classif'':25 ''contain'':6 ''data'':2,4 ''demograph'':17 ''donor'':11,29 ''fibrosi'':39 ''hcv'':1 ''hepat'':13,31,37 ''includ'':33 ''laboratori'':7 ''like'':19 ''patient'':15 ''progress'':35 ''set'':5 ''target'':22 ''valu'':8,18 ''vs'':30');
INSERT INTO public.datasets VALUES (41, 'uci', '572', 'Taiwanese Bankruptcy Prediction', 'The data were collected from the Taiwan Economic Journal  for the years 1999 to 2009. Company bankruptcy was defined based on the business regulations of the Taiwan Stock Exchange.', '{Business,Multivariate,Classification}', 'csv', 11187.60, 'active', 'https://archive.ics.uci.edu/static/public/572/taiwanese+bankruptcy+prediction.zip', 'https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction', '2024-03-15 00:00:00', '''1999'':16 ''2009'':18 ''bankruptci'':2,20 ''base'':23 ''busi'':26 ''collect'':7 ''compani'':19 ''data'':5 ''defin'':22 ''econom'':11 ''exchang'':32 ''journal'':12 ''predict'':3 ''regul'':27 ''stock'':31 ''taiwan'':10,30 ''taiwanes'':1 ''year'':15');
INSERT INTO public.datasets VALUES (42, 'uci', '591', 'Gender by Name', 'This dataset attributes first names to genders, giving counts and probabilities.  It combines open-source government data from the US, UK, Canada, and Australia.





This dataset combines raw counts for first/given names of male and female babies in those time periods, and then calculates a probability for a name given the aggregate count.  Source datasets are from government authorities:



-US: Baby Names from Social Security Card Applications - National Data, 1880 to 2019



-UK:  Baby names in England and Wales Statistical bulletins, 2011 to 2018



-Canada: British Columbia 100 Years of Popular Baby names, 1918 to 2018



-Australia:  Popular Baby Names, Attorney-General''s Department, 1944 to 2019', '{"Social Science",Text,Classification,Clustering}', 'csv', 3686.12, 'active', 'https://archive.ics.uci.edu/static/public/591/gender+by+name.zip', 'https://archive.ics.uci.edu/dataset/591/gender+by+name', '2024-03-28 00:00:00', '''100'':92 ''1880'':74 ''1918'':98 ''1944'':110 ''2011'':86 ''2018'':88,100 ''2019'':76,112 ''aggreg'':56 ''applic'':71 ''attorney'':106 ''attorney-gener'':105 ''attribut'':6 ''australia'':28,101 ''author'':63 ''babi'':41,65,78,96,103 ''british'':90 ''bulletin'':85 ''calcul'':48 ''canada'':26,89 ''card'':70 ''columbia'':91 ''combin'':16,31 ''count'':12,33,57 ''data'':21,73 ''dataset'':5,30,59 ''depart'':109 ''england'':81 ''femal'':40 ''first'':7 ''first/given'':35 ''gender'':1,10 ''general'':107 ''give'':11 ''given'':54 ''govern'':20,62 ''male'':38 ''name'':3,8,36,53,66,79,97,104 ''nation'':72 ''open'':18 ''open-sourc'':17 ''period'':45 ''popular'':95,102 ''probabl'':14,50 ''raw'':32 ''secur'':69 ''social'':68 ''sourc'':19,58 ''statist'':84 ''time'':44 ''uk'':25,77 ''us'':24,64 ''wale'':83 ''year'':93');
INSERT INTO public.datasets VALUES (43, 'uci', '597', 'Productivity Prediction of Garment Employees', 'This dataset includes important attributes of the garment manufacturing process and the productivity of the employees which had been collected manually and also been validated by the industry experts.



The Garment Industry is one of the key examples of the industrial globalization of this modern era. It is a highly labour-intensive industry with lots of manual processes. Satisfying the huge global demand for garment products is mostly dependent on the production and delivery performance of the employees in the garment manufacturing companies. So, it is highly desirable among the decision makers in the garments industry to track, analyse and predict the productivity performance of the working teams in their factories. This dataset can be used for regression purpose by predicting the productivity range (0-1) or for classification purpose by transforming the productivity range (0-1) into different classes.', '{Business,Multivariate,Time-Series,Classification,Regression}', 'csv', 92.71, 'active', 'https://archive.ics.uci.edu/static/public/597/productivity+prediction+of+garment+employees.zip', 'https://archive.ics.uci.edu/dataset/597/productivity+prediction+of+garment+employees', '2024-02-26 00:00:00', '''-1'':132,143 ''0'':131,142 ''also'':28 ''among'':95 ''analys'':105 ''attribut'':10 ''class'':146 ''classif'':135 ''collect'':25 ''compani'':89 ''dataset'':7,119 ''decis'':97 ''deliveri'':80 ''demand'':69 ''depend'':75 ''desir'':94 ''differ'':145 ''employe'':5,21,84 ''era'':51 ''exampl'':43 ''expert'':34 ''factori'':117 ''garment'':4,13,36,71,87,101 ''global'':47,68 ''high'':55,93 ''huge'':67 ''import'':9 ''includ'':8 ''industri'':33,37,46,59,102 ''intens'':58 ''key'':42 ''labour'':57 ''labour-intens'':56 ''lot'':61 ''maker'':98 ''manual'':26,63 ''manufactur'':14,88 ''modern'':50 ''most'':74 ''one'':39 ''perform'':81,110 ''predict'':2,107,127 ''process'':15,64 ''product'':1,18,72,78,109,129,140 ''purpos'':125,136 ''rang'':130,141 ''regress'':124 ''satisfi'':65 ''team'':114 ''track'':104 ''transform'':138 ''use'':122 ''valid'':30 ''work'':113');
INSERT INTO public.datasets VALUES (45, 'uci', '603', 'In-Vehicle Coupon Recommendation', 'This data studies whether a person will accept the coupon recommended to him in different driving scenarios



This data was collected via a survey on Amazon Mechanical Turk. The survey describes different driving scenarios including the destination, current time, weather, passenger, etc., and then ask the person whether they will accept the coupon if they are the driver. For more information about the dataset, please refer to the paper:

Wang, Tong, Cynthia Rudin, Finale Doshi-Velez, Yimin Liu, Erica Klampfl, and Perry MacNeille. ''A Bayesian framework for learning rule sets for interpretable classification.'' The Journal of Machine Learning Research 18, no. 1 (2017): 2357-2393.', '{Business,Multivariate,Classification}', 'csv', 2112.75, 'active', 'https://archive.ics.uci.edu/static/public/603/in+vehicle+coupon+recommendation.zip', 'https://archive.ics.uci.edu/dataset/603/in+vehicle+coupon+recommendation', '2025-09-19 00:00:00', '''-2393'':111 ''1'':108 ''18'':106 ''2017'':109 ''2357'':110 ''accept'':13,56 ''amazon'':31 ''ask'':50 ''bayesian'':91 ''classif'':99 ''collect'':26 ''coupon'':4,15,58 ''current'':43 ''cynthia'':77 ''data'':7,24 ''dataset'':69 ''describ'':36 ''destin'':42 ''differ'':20,37 ''doshi'':81 ''doshi-velez'':80 ''drive'':21,38 ''driver'':63 ''erica'':85 ''etc'':47 ''final'':79 ''framework'':92 ''in-vehicl'':1 ''includ'':40 ''inform'':66 ''interpret'':98 ''journal'':101 ''klampfl'':86 ''learn'':94,104 ''liu'':84 ''machin'':103 ''macneill'':89 ''mechan'':32 ''paper'':74 ''passeng'':46 ''perri'':88 ''person'':11,52 ''pleas'':70 ''recommend'':5,16 ''refer'':71 ''research'':105 ''rudin'':78 ''rule'':95 ''scenario'':22,39 ''set'':96 ''studi'':8 ''survey'':29,35 ''time'':44 ''tong'':76 ''turk'':33 ''vehicl'':3 ''velez'':82 ''via'':27 ''wang'':75 ''weather'':45 ''whether'':9,53 ''yimin'':83');
INSERT INTO public.datasets VALUES (46, 'uci', '697', 'Predict Students'' Dropout and Academic Success', 'A dataset created from a higher education institution (acquired from several disjoint databases) related to students enrolled in different undergraduate degrees, such as agronomy, design, education, nursing, journalism, management, social service, and technologies.

The dataset includes information known at the time of student enrollment (academic path, demographics, and social-economic factors) and the students'' academic performance at the end of the first and second semesters. 

The data is used to build classification models to predict students'' dropout and academic sucess. The problem is formulated as a three category classification task, in which there is a strong imbalance towards one of the classes.', '{"Social Science",Tabular,Classification}', 'csv', 520.73, 'active', 'https://archive.ics.uci.edu/static/public/697/predict+students+dropout+and+academic+success.zip', 'https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success', '2024-02-26 00:00:00', '''academ'':5,51,62,86 ''acquir'':15 ''agronomi'':30 ''build'':78 ''categori'':95 ''class'':109 ''classif'':79,96 ''creat'':9 ''data'':74 ''databas'':19 ''dataset'':8,41 ''degre'':27 ''demograph'':53 ''design'':31 ''differ'':25 ''disjoint'':18 ''dropout'':3,84 ''econom'':57 ''educ'':13,32 ''end'':66 ''enrol'':23,50 ''factor'':58 ''first'':69 ''formul'':91 ''higher'':12 ''imbal'':104 ''includ'':42 ''inform'':43 ''institut'':14 ''journal'':34 ''known'':44 ''manag'':35 ''model'':80 ''nurs'':33 ''one'':106 ''path'':52 ''perform'':63 ''predict'':1,82 ''problem'':89 ''relat'':20 ''second'':71 ''semest'':72 ''servic'':37 ''sever'':17 ''social'':36,56 ''social-econom'':55 ''strong'':103 ''student'':2,22,49,61,83 ''success'':6 ''sucess'':87 ''task'':97 ''technolog'':39 ''three'':94 ''time'':47 ''toward'':105 ''undergradu'':26 ''use'':76');
INSERT INTO public.datasets VALUES (47, 'uci', '713', 'Auction Verification', 'We modeled a simultaneous multi-round auction with BPMN models, transformed the latter to Petri nets, and used a model checker to verify whether certain outcomes of the auction are possible or not.



Our code to prepare the dataset and to make predictions is available here: https://github.com/Jakob-Bach/Analyzing-Auction-Verification', '{"Computer Science",Tabular,Classification,Regression}', 'csv', 74.66, 'active', 'https://archive.ics.uci.edu/static/public/713/auction+verification.zip', 'https://archive.ics.uci.edu/dataset/713/auction+verification', '2022-04-24 00:00:00', '''/jakob-bach/analyzing-auction-verification'':52 ''auction'':1,10,32 ''avail'':48 ''bpmn'':12 ''certain'':28 ''checker'':24 ''code'':38 ''dataset'':42 ''github.com'':51 ''github.com/jakob-bach/analyzing-auction-verification'':50 ''latter'':16 ''make'':45 ''model'':4,13,23 ''multi'':8 ''multi-round'':7 ''net'':19 ''outcom'':29 ''petri'':18 ''possibl'':34 ''predict'':46 ''prepar'':40 ''round'':9 ''simultan'':6 ''transform'':14 ''use'':21 ''verif'':2 ''verifi'':26 ''whether'':27');
INSERT INTO public.datasets VALUES (48, 'uci', '722', 'NATICUSdroid (Android Permissions)', 'Contains permissions extracted from more than 29000 benign & malware Android apps released between 2010-2019.', '{"Computer Science",Tabular,Classification}', 'csv', 5016.18, 'active', 'https://archive.ics.uci.edu/static/public/722/naticusdroid+android+permissions+dataset.zip', 'https://archive.ics.uci.edu/dataset/722/naticusdroid+android+permissions+dataset', '2024-04-09 00:00:00', '''-2019'':18 ''2010'':17 ''29000'':10 ''android'':2,13 ''app'':14 ''benign'':11 ''contain'':4 ''extract'':6 ''malwar'':12 ''naticusdroid'':1 ''permiss'':3,5 ''releas'':15');
INSERT INTO public.datasets VALUES (49, 'uci', '728', 'Toxicity', 'The dataset includes 171 molecules designed for functional domains of a core clock protein, CRY1, responsible for generating circadian rhythm. 56 of the molecules are toxic and the rest are non-toxic.', '{Biology,Tabular,Classification}', 'csv', 1254.57, 'active', 'https://archive.ics.uci.edu/static/public/728/toxicity-2.zip', 'https://archive.ics.uci.edu/dataset/728/toxicity-2', '2022-05-05 00:00:00', '''171'':5 ''56'':22 ''circadian'':20 ''clock'':14 ''core'':13 ''cry1'':16 ''dataset'':3 ''design'':7 ''domain'':10 ''function'':9 ''generat'':19 ''includ'':4 ''molecul'':6,25 ''non'':33 ''non-tox'':32 ''protein'':15 ''respons'':17 ''rest'':30 ''rhythm'':21 ''toxic'':1,27,34');
INSERT INTO public.datasets VALUES (50, 'uci', '732', 'DARWIN', 'The DARWIN dataset includes handwriting data from 174 participants. The classification task consists in distinguishing Alzheimer╤В╨Р╨йs disease patients from healthy people.', '{"Health and Medicine",Tabular,Classification}', 'csv', 1055.27, 'active', 'https://archive.ics.uci.edu/static/public/732/darwin.zip', 'https://archive.ics.uci.edu/dataset/732/darwin', '2023-11-03 00:00:00', '''174'':9 ''alzheimer╤В╨░╤Й'':17 ''classif'':12 ''consist'':14 ''darwin'':1,3 ''data'':7 ''dataset'':4 ''diseas'':18 ''distinguish'':16 ''handwrit'':6 ''healthi'':21 ''includ'':5 ''particip'':10 ''patient'':19 ''peopl'':22 ''task'':13');
INSERT INTO public.datasets VALUES (51, 'uci', '755', 'Accelerometer Gyro Mobile Phone', 'data collected on 2022, in King Saud University in riyadh for recognizing human activities using mobile phone IMU sensors (Accelerometer, and Gyroscope). these activity is calssified to standing(stop), or walking.', '{"Computer Science",Tabular,Sequential,Multivariate,Time-Series,Classification}', 'csv', 2085.14, 'active', 'https://archive.ics.uci.edu/static/public/755/accelerometer+gyro+mobile+phone+dataset.zip', 'https://archive.ics.uci.edu/dataset/755/accelerometer+gyro+mobile+phone+dataset', '2024-04-09 00:00:00', '''2022'':8 ''acceleromet'':1,24 ''activ'':18,28 ''calssifi'':30 ''collect'':6 ''data'':5 ''gyro'':2 ''gyroscop'':26 ''human'':17 ''imu'':22 ''king'':10 ''mobil'':3,20 ''phone'':4,21 ''recogn'':16 ''riyadh'':14 ''saud'':11 ''sensor'':23 ''stand'':32 ''stop'':33 ''univers'':12 ''use'':19 ''walk'':35');
INSERT INTO public.datasets VALUES (53, 'uci', '760', 'Multivariate Gait Data', 'Bilateral (left, right) joint angle (ankle, knee, hip) times series data collected from 10 healthy subjects under 3 walking conditions (unbraced, knee braced, ankle braced). For each condition, each subject╤В╨Р╨йs data consists of 10 consecutive gait cycles.



This dataset is a six dimensional array of joint angle data: 10 subjects x 3 conditions x 10 replications x 2 legs x 3 joints x 101 time points. The data were recored from ten subjects under three different conditions: normal (unbraced) walking on a treadmill, walking on a treadmill with a knee-brace on the right knee, and walking on a treadmill with an ankle brace on the right ankle. For each subject in each condition, ten consecutive gait cycles (replications) are included, where each gait cycle starts and ends at heel-strike. For each gait cycle, the data were normalized to consist of 101 time points representing 0%,╤В╨Р╨╢,100% of the gait cycle. Six joint angles are included, which comprise all combinations of leg (left and right) and joint (ankle, knee, hip). The data were collected at the Human Dynamics and Controls Laboratory at the University of Illinois at Urbana-Champaign. Details of the experimental setup can be found in Shorter et al. (2008). Details on the data preprocessing can be found in Helwig et al. (2011). The data were published as supplementary materials by Helwig et al. (2016). 



Attribute Information:

1. subject: 1 = subject 1, ╤В╨Р╨╢, 10 = subject 10 (integer)

2. condition: 1 = unbraced, 2 = knee brace, 3 = ankle brace (integer)

3. replication: 1 = replication 1, ╤В╨Р╨╢, 10 = replication 10 (integer)

4. leg: 1 = left, 2 = right (integer)

5. joint: 1 = ankle, 2 = knee, 3 = hip (integer)

6. time: 0 = 0% gait cycle, ╤В╨Р╨╢, 100 = 100% gait cycle (integer)

7. angle: joint angle in degrees (real valued)', '{"Health and Medicine",Sequential,Multivariate,Time-Series,Classification,Regression,Clustering}', 'csv', 5372.95, 'active', 'https://archive.ics.uci.edu/static/public/760/multivariate+gait+data.zip', 'https://archive.ics.uci.edu/dataset/760/multivariate+gait+data', '2024-03-20 00:00:00', '''0'':152,287,288 ''1'':238,240,242,250,261,263,271,278 ''10'':17,37,52,58,244,246,265,267 ''100'':154,292,293 ''101'':67,148 ''2'':61,248,252,273,280 ''2008'':210 ''2011'':223 ''2016'':235 ''3'':21,55,64,255,259,282 ''4'':269 ''5'':276 ''6'':285 ''7'':297 ''al'':209,222,234 ''angl'':8,50,161,298,300 ''ankl'':9,27,107,112,175,256,279 ''array'':47 ''attribut'':236 ''bilater'':4 ''brace'':26,28,95,108,254,257 ''champaign'':197 ''collect'':15,181 ''combin'':167 ''compris'':165 ''condit'':23,31,56,80,118,249 ''consecut'':38,120 ''consist'':35,146 ''control'':187 ''cycl'':40,122,129,140,158,290,295 ''data'':3,14,34,51,71,142,179,214,225 ''dataset'':42 ''degre'':302 ''detail'':198,211 ''differ'':79 ''dimension'':46 ''dynam'':185 ''end'':132 ''et'':208,221,233 ''experiment'':201 ''found'':205,218 ''gait'':2,39,121,128,139,157,289,294 ''healthi'':18 ''heel'':135 ''heel-strik'':134 ''helwig'':220,232 ''hip'':11,177,283 ''human'':184 ''illinoi'':193 ''includ'':125,163 ''inform'':237 ''integ'':247,258,268,275,284,296 ''joint'':7,49,65,160,174,277,299 ''knee'':10,25,94,99,176,253,281 ''knee-brac'':93 ''laboratori'':188 ''left'':5,170,272 ''leg'':62,169,270 ''materi'':230 ''multivari'':1 ''normal'':81,144 ''point'':69,150 ''preprocess'':215 ''publish'':227 ''real'':303 ''recor'':73 ''replic'':59,123,260,262,266 ''repres'':151 ''right'':6,98,111,172,274 ''seri'':13 ''setup'':202 ''shorter'':207 ''six'':45,159 ''start'':130 ''strike'':136 ''subject'':19,53,76,115,239,241,245 ''subject╤В╨░╤Й'':33 ''supplementari'':229 ''ten'':75,119 ''three'':78 ''time'':12,68,149,286 ''treadmil'':86,90,104 ''unbrac'':24,82,251 ''univers'':191 ''urbana'':196 ''urbana-champaign'':195 ''valu'':304 ''walk'':22,83,87,101 ''x'':54,57,60,63,66 ''╤В╨░╨╢'':153,243,264,291');
INSERT INTO public.datasets VALUES (54, 'uci', '799', 'Single Elder Home Monitoring: Gas and Position', 'This dataset contains gas and temperature sensors as well as movement infra-red sensors from the monitoring of an elder person living alone in their own home from 2019-11-06 to 2020-02-13. The measurings have a temporal resolution of 20 seconds. The air and gas sensors measure temperature, humidity, CO2, CO and MOX readings. The data from the position sensors are binary; for each room, a 1 means that movement has been detected in that room while a 0 means that the sensor has gone back to baseline. The attached figure represents a simple layout of the monitored home as well as the sensors locations. The dataset also includes 19 days of measurements (from 2020-01-25 to 2020-02-13) where noone was occupying the room (except for an esporadic visit the 2020-01-29 at 15:), as reference data', '{Engineering,Tabular,Classification}', 'csv', 43072.43, 'active', 'https://archive.ics.uci.edu/static/public/799/single+elder+home+monitoring+gas+and+position.zip', 'https://archive.ics.uci.edu/dataset/799/single+elder+home+monitoring+gas+and+position', '2024-04-09 00:00:00', '''-01'':127,146 ''-02'':42,131 ''-06'':39 ''-11'':38 ''-13'':43,132 ''-25'':128 ''-29'':147 ''0'':90 ''1'':78 ''15'':149 ''19'':121 ''20'':51 ''2019'':37 ''2020'':41,126,130,145 ''air'':54 ''alon'':31 ''also'':119 ''attach'':101 ''back'':97 ''baselin'':99 ''binari'':73 ''co'':62 ''co2'':61 ''contain'':10 ''data'':67,152 ''dataset'':9,118 ''day'':122 ''detect'':84 ''elder'':2,28 ''esporad'':142 ''except'':139 ''figur'':102 ''gas'':5,11,56 ''gone'':96 ''home'':3,35,110 ''humid'':60 ''includ'':120 ''infra'':20 ''infra-r'':19 ''layout'':106 ''live'':30 ''locat'':116 ''mean'':79,91 ''measur'':45,58,124 ''monitor'':4,25,109 ''movement'':18,81 ''mox'':64 ''noon'':134 ''occupi'':136 ''person'':29 ''posit'':7,70 ''read'':65 ''red'':21 ''refer'':151 ''repres'':103 ''resolut'':49 ''room'':76,87,138 ''second'':52 ''sensor'':14,22,57,71,94,115 ''simpl'':105 ''singl'':1 ''temperatur'':13,59 ''tempor'':48 ''visit'':143 ''well'':16,112');
INSERT INTO public.datasets VALUES (55, 'kaggle', 'rebrowser/shopee-dataset', 'Shopee Product Listings Dataset', 'All Shopee domains are supported: Shopee.sg (Singapore), Shopee.my (Malaysia), Shopee.ph (Philippines), Shopee.vn (Vietnam), Shopee.id (Indonesia), Shopee.th (Thailand), Shopee.tw (Taiwan), Shopee.br (Brazil), and Shopee.mx (Mexico). Shopee is a sophisticated target and requires a more custom approach, please contact us for details and tailored options.



Our datasets can include historical product listings, seller metadata, and promotion activity across categories, ideal for trend analysis, competitor research, and training product recommendation or pricing algorithms.', '{tabular,text}', 'csv', 76381.86, 'active', 'https://www.kaggle.com/api/v1/datasets/download/rebrowser/shopee-dataset', 'https://www.kaggle.com/datasets/rebrowser/shopee-dataset', '2026-03-20 17:04:05.29', '''across'':60 ''activ'':59 ''algorithm'':74 ''analysi'':65 ''approach'':39 ''brazil'':25 ''categori'':61 ''competitor'':66 ''contact'':41 ''custom'':38 ''dataset'':4,49 ''detail'':44 ''domain'':7 ''histor'':52 ''ideal'':62 ''includ'':51 ''indonesia'':19 ''list'':3,54 ''malaysia'':13 ''metadata'':56 ''mexico'':28 ''option'':47 ''philippin'':15 ''pleas'':40 ''price'':73 ''product'':2,53,70 ''promot'':58 ''recommend'':71 ''requir'':35 ''research'':67 ''seller'':55 ''shope'':1,6,29 ''shopee.br'':24 ''shopee.id'':18 ''shopee.mx'':27 ''shopee.my'':12 ''shopee.ph'':14 ''shopee.sg'':10 ''shopee.th'':20 ''shopee.tw'':22 ''shopee.vn'':16 ''singapor'':11 ''sophist'':32 ''support'':9 ''tailor'':46 ''taiwan'':23 ''target'':33 ''thailand'':21 ''train'':69 ''trend'':64 ''us'':42 ''vietnam'':17');
INSERT INTO public.datasets VALUES (56, 'kaggle', 'rebrowser/iheart-dataset', 'iHeart Radio Stations & Airplay Dataset', 'Access comprehensive datasets containing thousands of iHeart radio station profiles with call letters, frequencies, formats, market data, audience metrics, and historical programming changes. Our curated datasets cover the full iHeart network across AM, FM, HD Radio, and digital-only broadcasts.



Accelerate your radio industry research with pre-processed iHeart data including station plays history, format change tracking, and audience reach estimates. Perfect for media planners, music industry analysts, and researchers studying US broadcast radio trends.', '{music,"united states",tabular,text}', 'csv', 151879.79, 'active', 'https://www.kaggle.com/api/v1/datasets/download/rebrowser/iheart-dataset', 'https://www.kaggle.com/datasets/rebrowser/iheart-dataset', '2026-03-20 17:01:35.92', '''acceler'':47 ''access'':6 ''across'':37 ''airplay'':4 ''analyst'':75 ''audienc'':23,66 ''broadcast'':46,80 ''call'':17 ''chang'':28,63 ''comprehens'':7 ''contain'':9 ''cover'':32 ''curat'':30 ''data'':22,57 ''dataset'':5,8,31 ''digit'':44 ''digital-on'':43 ''estim'':68 ''fm'':39 ''format'':20,62 ''frequenc'':19 ''full'':34 ''hd'':40 ''histor'':26 ''histori'':61 ''iheart'':1,12,35,56 ''includ'':58 ''industri'':50,74 ''letter'':18 ''market'':21 ''media'':71 ''metric'':24 ''music'':73 ''network'':36 ''perfect'':69 ''planner'':72 ''play'':60 ''pre'':54 ''pre-process'':53 ''process'':55 ''profil'':15 ''program'':27 ''radio'':2,13,41,49,81 ''reach'':67 ''research'':51,77 ''station'':3,14,59 ''studi'':78 ''thousand'':10 ''track'':64 ''trend'':82 ''us'':79');
INSERT INTO public.datasets VALUES (57, 'uci', '849', 'Power Consumption of Tetouan City', 'This dataset is related to power consumption of three different distribution networks of Tetouan city which is located in north Morocco.', '{"Social Science",Multivariate,Time-Series,Regression}', 'csv', 4123.43, 'active', 'https://archive.ics.uci.edu/static/public/849/power+consumption+of+tetouan+city.zip', 'https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city', '2024-03-08 00:00:00', '''citi'':5,20 ''consumpt'':2,12 ''dataset'':7 ''differ'':15 ''distribut'':16 ''locat'':23 ''morocco'':26 ''network'':17 ''north'':25 ''power'':1,11 ''relat'':9 ''tetouan'':4,19 ''three'':14');
INSERT INTO public.datasets VALUES (58, 'uci', '851', 'Steel Industry Energy Consumption', 'The data is collected from a smart small-scale steel industry in South Korea.



The information gathered is from the DAEWOO Steel Co. Ltd in Gwangyang, South Korea. It produces several types of coils, steel plates, and iron plates. The information on electricity consumption is held in a cloud-based system. The information on energy consumption of the industry is stored on the website of the Korea Electric Power Corporation (pccs.kepco.go.kr), and the perspectives on daily, monthly, and annual data are calculated and shown.', '{"Physics and Chemistry",Multivariate,Regression}', 'csv', 2667.37, 'active', 'https://archive.ics.uci.edu/static/public/851/steel+industry+energy+consumption.zip', 'https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption', '2023-08-14 00:00:00', '''annual'':85 ''base'':56 ''calcul'':88 ''cloud'':55 ''cloud-bas'':54 ''co'':28 ''coil'':39 ''collect'':8 ''consumpt'':4,49,62 ''corpor'':76 ''daewoo'':26 ''daili'':82 ''data'':6,86 ''electr'':48,74 ''energi'':3,61 ''gather'':22 ''gwangyang'':31 ''held'':51 ''industri'':2,16,65 ''inform'':21,46,59 ''iron'':43 ''korea'':19,33,73 ''ltd'':29 ''month'':83 ''pccs.kepco.go.kr'':77 ''perspect'':80 ''plate'':41,44 ''power'':75 ''produc'':35 ''scale'':14 ''sever'':36 ''shown'':90 ''small'':13 ''small-scal'':12 ''smart'':11 ''south'':18,32 ''steel'':1,15,27,40 ''store'':67 ''system'':57 ''type'':37 ''websit'':70');
INSERT INTO public.datasets VALUES (59, 'uci', '856', 'Higher Education Students Performance Evaluation', 'The data was collected from the Faculty of Engineering and Faculty of Educational Sciences students in 2019. The purpose is to predict students'' end-of-term performances using ML techniques.



1-10 of the data are the personal questions, 11-16. questions include family questions, and the remaining questions include education habits.', '{"Social Science",Multivariate,Classification}', 'csv', 10.77, 'active', 'https://archive.ics.uci.edu/static/public/856/higher+education+students+performance+evaluation.zip', 'https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation', '2024-03-07 00:00:00', '''-10'':38 ''-16'':47 ''1'':37 ''11'':46 ''2019'':22 ''collect'':9 ''data'':7,41 ''educ'':2,18,57 ''end'':30 ''end-of-term'':29 ''engin'':14 ''evalu'':5 ''faculti'':12,16 ''famili'':50 ''habit'':58 ''higher'':1 ''includ'':49,56 ''ml'':35 ''perform'':4,33 ''person'':44 ''predict'':27 ''purpos'':24 ''question'':45,48,51,55 ''remain'':54 ''scienc'':19 ''student'':3,20,28 ''techniqu'':36 ''term'':32 ''use'':34');
INSERT INTO public.datasets VALUES (60, 'uci', '857', 'Risk Factor Prediction of Chronic Kidney Disease', 'Chronic kidney disease (CKD) is an increasing medical issue that declines the productivity of renal capacities and subsequently damages the kidneys.



This dataset is real Bangladeshi patient data. The dataset is collected from Enam Medical College, Savar, Dhaka, Bangladesh.', '{"Health and Medicine",Multivariate,Classification,Regression}', 'csv', 33.35, 'active', 'https://archive.ics.uci.edu/static/public/857/risk+factor+prediction+of+chronic+kidney+disease.zip', 'https://archive.ics.uci.edu/dataset/857/risk+factor+prediction+of+chronic+kidney+disease', '2024-03-08 00:00:00', '''bangladesh'':46 ''bangladeshi'':33 ''capac'':23 ''chronic'':5,8 ''ckd'':11 ''collect'':39 ''colleg'':43 ''damag'':26 ''data'':35 ''dataset'':30,37 ''declin'':18 ''dhaka'':45 ''diseas'':7,10 ''enam'':41 ''factor'':2 ''increas'':14 ''issu'':16 ''kidney'':6,9,28 ''medic'':15,42 ''patient'':34 ''predict'':3 ''product'':20 ''real'':32 ''renal'':22 ''risk'':1 ''savar'':44 ''subsequ'':25');
INSERT INTO public.datasets VALUES (61, 'uci', '863', 'Maternal Health Risk', 'Data has been collected from different hospitals, community clinics, maternal health cares from the rural areas of Bangladesh through the IoT based risk monitoring system.



Age, Systolic Blood Pressure as SystolicBP, Diastolic BP as DiastolicBP, Blood Sugar as BS, Body Temperature as BodyTemp, HeartRate and RiskLevel. All these are the responsible and significant risk factors for maternal mortality, that is one of the main concern of SDG of UN.', '{"Health and Medicine",Multivariate,Classification}', 'csv', 29.58, 'active', 'https://archive.ics.uci.edu/static/public/863/maternal+health+risk.zip', 'https://archive.ics.uci.edu/dataset/863/maternal+health+risk', '2023-11-03 00:00:00', '''age'':29 ''area'':19 ''bangladesh'':21 ''base'':25 ''blood'':31,39 ''bodi'':43 ''bodytemp'':46 ''bp'':36 ''bs'':42 ''care'':15 ''clinic'':12 ''collect'':7 ''communiti'':11 ''concern'':68 ''data'':4 ''diastol'':35 ''diastolicbp'':38 ''differ'':9 ''factor'':58 ''health'':2,14 ''heartrat'':47 ''hospit'':10 ''iot'':24 ''main'':67 ''matern'':1,13,60 ''monitor'':27 ''mortal'':61 ''one'':64 ''pressur'':32 ''respons'':54 ''risk'':3,26,57 ''risklevel'':49 ''rural'':18 ''sdg'':70 ''signific'':56 ''sugar'':40 ''system'':28 ''systol'':30 ''systolicbp'':34 ''temperatur'':44 ''un'':72');
INSERT INTO public.datasets VALUES (62, 'uci', '864', 'Room Occupancy Estimation', 'Data set for estimating the precise number of occupants in a room using multiple non-intrusive environmental sensors like temperature, light, sound, CO2 and PIR.



The experimental testbed for occupancy estimation was deployed in a 6m x 4.6m room. The setup consisted of 7 sensor nodes and one edge node in a star configuration with the sensor nodes transmitting data to the edge every 30s using wireless transceivers. No HVAC systems were in use while the dataset was being collected.



Five different types of non-intrusive sensors were used in this experiment: temperature, light, sound, CO2 and digital passive infrared (PIR). The CO2, sound and PIR sensors needed manual calibration. For the CO2 sensor, zero-point calibration was manually done before its first use by keeping it in a clean environment for over 20 minutes and then pulling the calibration pin (HD pin) low for over 7s. The sound sensor is essentially a microphone with a variable-gain analog amplifier attached to it. Therefore, the output of this sensor is analog which is read by the microcontrollerтФЬ╨▓╤В╨Т╨╝╤В╨Ф╨▓s ADC in volts. The potentiometer tied to the gain of the amplifier was adjusted to ensure the highest sensitivity. The PIR sensor has two trimpots: one to tweak the sensitivity and the other to tweak the time for which the output stays high after detecting motion. Both of these were adjusted to the highest values. Sensor nodes S1-S4 consisted of temperature, light and sound sensors, S5 had a CO2 sensor and S6 and S7 had one PIR sensor each that were deployed on the ceiling ledges at an angle that maximized the sensorтФЬ╨▓╤В╨Т╨╝╤В╨Ф╨▓s field of view for motion detection.



The data was collected for a period of 4 days in a controlled manner with the occupancy in the room varying between 0 and 3 people. The ground truth of the occupancy count in the room was noted manually.



Please refer to our publications for more details.', '{"Computer Science",Multivariate,Time-Series,Classification}', 'csv', 909.79, 'active', 'https://archive.ics.uci.edu/static/public/864/room+occupancy+estimation.zip', 'https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation', '2023-08-16 00:00:00', '''0'':311 ''20'':141 ''3'':313 ''30s'':70 ''4'':297 ''4.6'':42 ''6m'':40 ''7'':49 ''7s'':154 ''adc'':187 ''adjust'':200,237 ''amplifi'':168,198 ''analog'':167,179 ''angl'':277 ''attach'':169 ''calibr'':116,124,147 ''ceil'':273 ''clean'':137 ''co2'':27,102,109,119,257 ''collect'':85,292 ''configur'':59 ''consist'':47,247 ''control'':301 ''count'':321 ''data'':4,65,290 ''dataset'':82 ''day'':298 ''deploy'':37,270 ''detail'':335 ''detect'':231,288 ''differ'':87 ''digit'':104 ''done'':127 ''edg'':54,68 ''ensur'':202 ''environ'':138 ''environment'':21 ''essenti'':159 ''estim'':3,7,35 ''everi'':69 ''experi'':98 ''experiment'':31 ''field'':283 ''first'':130 ''five'':86 ''gain'':166,195 ''ground'':316 ''hd'':149 ''high'':229 ''highest'':204,240 ''hvac'':75 ''infrar'':106 ''intrus'':20,92 ''keep'':133 ''ledg'':274 ''light'':25,100,250 ''like'':23 ''low'':151 ''m'':43 ''manner'':302 ''manual'':115,126,327 ''maxim'':279 ''microcontrol'':185 ''microphon'':161 ''minut'':142 ''motion'':232,287 ''multipl'':17 ''need'':114 ''node'':51,55,63,243 ''non'':19,91 ''non-intrus'':18,90 ''note'':326 ''number'':10 ''occup'':2,12,34,305,320 ''one'':53,212,264 ''output'':174,227 ''passiv'':105 ''peopl'':314 ''period'':295 ''pin'':148,150 ''pir'':29,107,112,207,265 ''pleas'':328 ''point'':123 ''potentiomet'':191 ''precis'':9 ''public'':332 ''pull'':145 ''read'':182 ''refer'':329 ''room'':1,15,44,308,324 ''s1'':245 ''s1-s4'':244 ''s4'':246 ''s5'':254 ''s6'':260 ''s7'':262 ''sensit'':205,216 ''sensor'':22,50,62,93,113,120,157,177,208,242,253,258,266,281 ''set'':5 ''setup'':46 ''sound'':26,101,110,156,252 ''star'':58 ''stay'':228 ''system'':76 ''temperatur'':24,99,249 ''testb'':32 ''therefor'':172 ''tie'':192 ''time'':223 ''transceiv'':73 ''transmit'':64 ''trimpot'':211 ''truth'':317 ''tweak'':214,221 ''two'':210 ''type'':88 ''use'':16,71,79,95,131 ''valu'':241 ''vari'':309 ''variabl'':165 ''variable-gain'':164 ''view'':285 ''volt'':189 ''wireless'':72 ''x'':41 ''zero'':122 ''zero-point'':121 ''╨▓╤В╨▓╨╝╤В╨┤╨▓s'':186,282');
INSERT INTO public.datasets VALUES (63, 'uci', '878', 'Cirrhosis Patient Survival Prediction', 'Utilize 17 clinical features for predicting survival state of patients with liver cirrhosis. The survival states include 0 = D (death), 1 = C (censored), 2 = CL (censored due to liver transplantation).



During 1974 to 1984, 424 PBC patients referred to the Mayo Clinic qualified for the randomized placebo-controlled trial testing the drug D-penicillamine. Of these, the initial 312 patients took part in the trial and have mostly comprehensive data. The remaining 112 patients didn''t join the clinical trial but agreed to record basic metrics and undergo survival tracking. Six of these patients were soon untraceable after their diagnosis, leaving data for 106 of these individuals in addition to the 312 who were part of the randomized trial.', '{"Health and Medicine",Tabular,Classification}', 'csv', 31.11, 'active', 'https://archive.ics.uci.edu/static/public/878/cirrhosis+patient+survival+prediction+dataset-1.zip', 'https://archive.ics.uci.edu/dataset/878/cirrhosis+patient+survival+prediction+dataset-1', '2023-11-03 00:00:00', '''0'':22 ''1'':25 ''106'':110 ''112'':79 ''17'':6 ''1974'':36 ''1984'':38 ''2'':28 ''312'':65,118 ''424'':39 ''addit'':115 ''agre'':88 ''basic'':91 ''c'':26 ''censor'':27,30 ''cirrhosi'':1,17 ''cl'':29 ''clinic'':7,46,85 ''comprehens'':75 ''control'':53 ''d'':23,59 ''d-penicillamin'':58 ''data'':76,108 ''death'':24 ''diagnosi'':106 ''didn'':81 ''drug'':57 ''due'':31 ''featur'':8 ''includ'':21 ''individu'':113 ''initi'':64 ''join'':83 ''leav'':107 ''liver'':16,33 ''mayo'':45 ''metric'':92 ''most'':74 ''part'':68,121 ''patient'':2,14,41,66,80,100 ''pbc'':40 ''penicillamin'':60 ''placebo'':52 ''placebo-control'':51 ''predict'':4,10 ''qualifi'':47 ''random'':50,124 ''record'':90 ''refer'':42 ''remain'':78 ''six'':97 ''soon'':102 ''state'':12,20 ''surviv'':3,11,19,95 ''test'':55 ''took'':67 ''track'':96 ''transplant'':34 ''trial'':54,71,86,125 ''undergo'':94 ''untrac'':103 ''util'':5');
INSERT INTO public.datasets VALUES (64, 'uci', '911', 'Recipe Reviews and User Feedback', 'The "Recipe Reviews and User Feedback Dataset" is a comprehensive repository of data encompassing various aspects of recipe reviews and user interactions. It includes essential information such as the recipe name, its ranking on the top 100 recipes list, a unique recipe code, and user details like user ID, user name, and an internal user reputation score.



Each review comment is uniquely identified with a comment ID and comes with additional attributes, including the creation timestamp, reply count, and the number of up-votes and down-votes received. Users'' sentiment towards recipes is quantified on a 1 to 5 star rating scale, with a score of 0 denoting an absence of rating.



This dataset is a valuable resource for researchers and data scientists, facilitating endeavors in sentiment analysis, user behavior analysis, recipe recommendation systems, and more. It offers a window into the dynamics of recipe reviews and user feedback within the culinary website domain.', '{"Computer Science",Tabular,Other,Classification}', 'csv', 5949.86, 'active', 'https://archive.ics.uci.edu/static/public/911/recipe+reviews+and+user+feedback+dataset.zip', 'https://archive.ics.uci.edu/dataset/911/recipe+reviews+and+user+feedback+dataset', '2024-03-08 00:00:00', '''0'':114 ''1'':104 ''100'':42 ''5'':106 ''absenc'':117 ''addit'':76 ''analysi'':135,138 ''aspect'':21 ''attribut'':77 ''behavior'':137 ''code'':48 ''come'':74 ''comment'':65,71 ''comprehens'':15 ''count'':83 ''creation'':80 ''culinari'':159 ''data'':18,129 ''dataset'':12,121 ''denot'':115 ''detail'':51 ''domain'':161 ''down-vot'':92 ''dynam'':150 ''encompass'':19 ''endeavor'':132 ''essenti'':30 ''facilit'':131 ''feedback'':5,11,156 ''id'':54,72 ''identifi'':68 ''includ'':29,78 ''inform'':31 ''interact'':27 ''intern'':59 ''like'':52 ''list'':44 ''name'':36,56 ''number'':86 ''offer'':145 ''quantifi'':101 ''rank'':38 ''rate'':108,119 ''receiv'':95 ''recip'':1,7,23,35,43,47,99,139,152 ''recommend'':140 ''repli'':82 ''repositori'':16 ''reput'':61 ''research'':127 ''resourc'':125 ''review'':2,8,24,64,153 ''scale'':109 ''scientist'':130 ''score'':62,112 ''sentiment'':97,134 ''star'':107 ''system'':141 ''timestamp'':81 ''top'':41 ''toward'':98 ''uniqu'':46,67 ''up-vot'':88 ''user'':4,10,26,50,53,55,60,96,136,155 ''valuabl'':124 ''various'':20 ''vote'':90,94 ''websit'':160 ''window'':147 ''within'':157');
INSERT INTO public.datasets VALUES (65, 'uci', '913', 'Forty Soybean Cultivars from Subsequent Harvests', 'Soybean cultivation is one of the most important because it is used in several segments of the food industry. The evaluation of soybean cultivars subject to different planting and harvesting characteristics is an ongoing field of research. We present a dataset obtained from forty soybean cultivars planted in subsequent seasons. The experiment used randomized blocks, arranged in a split-plot scheme, with four replications. The following variables were collected: plant height, insertion of the first pod, number of stems, number of legumes per plant, number of grains per pod, thousand seed weight, and grain yield, resulting in 320 data samples. The dataset presented can be used by researchers from different fields of activity.



More details about the dataset can be found in the published article: https://editorapantanal.com.br/journal/index.php/taes/article/view/8/5', '{Other,Tabular,Classification,Regression,Clustering}', 'csv', 26.80, 'active', 'https://archive.ics.uci.edu/static/public/913/forty+soybean+cultivars+from+subsequent+harvests.zip', 'https://archive.ics.uci.edu/dataset/913/forty+soybean+cultivars+from+subsequent+harvests', '2024-06-06 00:00:00', '''/journal/index.php/taes/article/view/8/5'':135 ''320'':105 ''activ'':120 ''arrang'':62 ''articl'':132 ''block'':61 ''characterist'':37 ''collect'':76 ''cultiv'':8 ''cultivar'':3,30,52 ''data'':106 ''dataset'':47,109,125 ''detail'':122 ''differ'':33,117 ''editorapantanal.com.br'':134 ''editorapantanal.com.br/journal/index.php/taes/article/view/8/5'':133 ''evalu'':27 ''experi'':58 ''field'':41,118 ''first'':82 ''follow'':73 ''food'':24 ''forti'':1,50 ''found'':128 ''four'':70 ''grain'':94,101 ''harvest'':6,36 ''height'':78 ''import'':14 ''industri'':25 ''insert'':79 ''legum'':89 ''number'':84,87,92 ''obtain'':48 ''one'':10 ''ongo'':40 ''per'':90,95 ''plant'':34,53,77,91 ''plot'':67 ''pod'':83,96 ''present'':45,110 ''publish'':131 ''random'':60 ''replic'':71 ''research'':43,115 ''result'':103 ''sampl'':107 ''scheme'':68 ''season'':56 ''seed'':98 ''segment'':21 ''sever'':20 ''soybean'':2,7,29,51 ''split'':66 ''split-plot'':65 ''stem'':86 ''subject'':31 ''subsequ'':5,55 ''thousand'':97 ''use'':18,59,113 ''variabl'':74 ''weight'':99 ''yield'':102');
INSERT INTO public.datasets VALUES (66, 'uci', '915', 'Differentiated Thyroid Cancer Recurrence', 'This data set contains 13 clinicopathologic features aiming to predict recurrence of well differentiated thyroid cancer. The data set was collected in duration of 15 years and each patient was followed for at least 10 years.', '{"Health and Medicine",Tabular,Classification}', 'csv', 42.57, 'active', 'https://archive.ics.uci.edu/static/public/915/differentiated+thyroid+cancer+recurrence.zip', 'https://archive.ics.uci.edu/dataset/915/differentiated+thyroid+cancer+recurrence', '2024-03-20 00:00:00', '''10'':39 ''13'':9 ''15'':29 ''aim'':12 ''cancer'':3,20 ''clinicopatholog'':10 ''collect'':25 ''contain'':8 ''data'':6,22 ''differenti'':1,18 ''durat'':27 ''featur'':11 ''follow'':35 ''least'':38 ''patient'':33 ''predict'':14 ''recurr'':4,15 ''set'':7,23 ''thyroid'':2,19 ''well'':17 ''year'':30,40');
INSERT INTO public.datasets VALUES (67, 'uci', '936', 'National Poll on Healthy Aging (NPHA)', 'This is a subset of the NPHA dataset filtered down to develop and validate machine learning algorithms for predicting the number of doctors a survey respondent sees in a year. This dataset╤В╨Р╨йs records represent seniors who responded to the NPHA survey.

', '{"Health and Medicine",Tabular,Classification}', 'csv', 21.26, 'active', 'https://archive.ics.uci.edu/static/public/936/national+poll+on+healthy+aging+(npha).zip', 'https://archive.ics.uci.edu/dataset/936/national+poll+on+healthy+aging+(npha)', '2023-12-11 00:00:00', '''age'':5 ''algorithm'':23 ''dataset'':14 ''dataset╤В╨░╤Й'':38 ''develop'':18 ''doctor'':29 ''filter'':15 ''healthi'':4 ''learn'':22 ''machin'':21 ''nation'':1 ''npha'':6,13,46 ''number'':27 ''poll'':2 ''predict'':25 ''record'':39 ''repres'':40 ''respond'':32,43 ''see'':33 ''senior'':41 ''subset'':10 ''survey'':31,47 ''valid'':20 ''year'':36');
INSERT INTO public.datasets VALUES (70, 'uci', '967', 'PhiUSIIL Phishing URL (Website)', 'PhiUSIIL Phishing URL Dataset is a substantial dataset comprising 134,850 legitimate and 100,945 phishing URLs. Most of the URLs we analyzed, while constructing the dataset, are the latest URLs. Features are extracted from the source code of the webpage and URL. Features such as CharContinuationRate, URLTitleMatchScore, URLCharProb, and TLDLegitimateProb are derived from existing features.', '{"Computer Science",Tabular,Classification}', 'csv', 55521.82, 'active', 'https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip', 'https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset', '2024-05-12 00:00:00', '''100'':18 ''134'':14 ''850'':15 ''945'':19 ''analyz'':27 ''charcontinuationr'':51 ''code'':42 ''compris'':13 ''construct'':29 ''dataset'':8,12,31 ''deriv'':57 ''exist'':59 ''extract'':38 ''featur'':36,48,60 ''latest'':34 ''legitim'':16 ''phish'':2,6,20 ''phiusiil'':1,5 ''sourc'':41 ''substanti'':11 ''tldlegitimateprob'':55 ''url'':3,7,21,25,35,47 ''urlcharprob'':53 ''urltitlematchscor'':52 ''webpag'':45 ''websit'':4');
INSERT INTO public.datasets VALUES (68, 'kaggle', 'kalilurrahman/atp-tennis-player-ranking-dataset', 'ATP Tour Ranking - Decade-wise and year-wise', 'The ATP Tour (known as the ATP World Tour from January 2009 until December 2018) is a worldwide top-tier tennis tour for men organized by the Association of Tennis Professionals. The second-tier tour is the ATP Challenger Tour and the third-tier is ITF Men''s World Tennis Tour. The equivalent women''s organisation is the WTA Tour.



The ATP Tour comprises ATP Masters 1000, ATP 500, and ATP 250.[1] The ATP also oversees the ATP Challenger Tour,[2] a level below the ATP Tour, and the ATP Champions Tour for seniors. Grand Slam tournaments, a small portion of the Olympic tennis tournament, the Davis Cup, and the entry-level ITF World Tennis Tour do not fall under the purview of the ATP, but are overseen by the ITF instead and the International Olympic Committee (IOC) for the Olympics. In these events, however, ATP ranking points are awarded, with the exception of the Olympics. The four-week ITF Satellite tournaments were discontinued in 2007. Players and doubles teams with the most ranking points (collected during the calendar year) play in the season-ending ATP Finals, which, from 2000╤В╨Р╨г2008, was run jointly with the International Tennis Federation (ITF). The details of the professional tennis tour are:



Event	Number	Total prize money (USD)	Winner''s ranking points	Governing body

Grand Slam	4	See individual articles	2,000	ITF

ATP Finals	1	4,450,000	1,100╤В╨Р╨г1,500	ATP (2009╤В╨Р╨гpresent)

ATP Masters 1000	9	2,450,000 to 3,645,000	1000	ATP

ATP 500	13	755,000 to 2,100,000	500	ATP

ATP 250	39	416,000 to 1,024,000	250	ATP

Olympics	1	See individual articles	0	IOC

ATP Challenger Tour	178	40,000 to 220,000	80 to 125	ATP

ITF Men''s Circuit	534	10,000 and 25,000	18 to 35	ITF



The dataset is from Jeff Sackmann(https://github.com/JeffSackmann/tennis_atp)', '{tennis,sports,"exploratory data analysis","data analytics",tabular}', 'csv', 77641.80, 'active', 'https://www.kaggle.com/api/v1/datasets/download/kalilurrahman/atp-tennis-player-ranking-dataset', 'https://www.kaggle.com/datasets/kalilurrahman/atp-tennis-player-ranking-dataset', '2026-03-18 15:46:26.507', '''/jeffsackmann/tennis_atp)'':334 ''0'':297 ''000'':244,251,263,267,274,278,285,289,304,307,318,321 ''024'':288 ''1'':86,248,252,287,293 ''10'':317 ''100'':277 ''1000'':80,259,268 ''100╤В╨░╤Г1'':253 ''125'':310 ''13'':272 ''178'':302 ''18'':322 ''2'':95,243,261,276 ''2000╤В╨░╤Г2008'':207 ''2007'':182 ''2009'':22 ''2009╤В╨░╤Гpresent'':256 ''2018'':25 ''220'':306 ''25'':320 ''250'':85,282,290 ''3'':265 ''35'':324 ''39'':283 ''4'':239,249 ''40'':303 ''416'':284 ''450'':250,262 ''500'':82,254,271,279 ''534'':316 ''645'':266 ''755'':273 ''80'':308 ''9'':260 ''also'':89 ''articl'':242,296 ''associ'':39 ''atp'':1,12,17,50,75,78,81,84,88,92,100,104,140,161,203,246,255,257,269,270,280,281,291,299,311 ''award'':165 ''bodi'':236 ''calendar'':195 ''challeng'':51,93,300 ''champion'':105 ''circuit'':315 ''collect'':192 ''committe'':152 ''compris'':77 ''cup'':122 ''dataset'':327 ''davi'':121 ''decad'':5 ''decade-wis'':4 ''decemb'':24 ''detail'':218 ''discontinu'':180 ''doubl'':185 ''end'':202 ''entri'':126 ''entry-level'':125 ''equival'':66 ''event'':159,225 ''except'':168 ''fall'':134 ''feder'':215 ''final'':204,247 ''four'':174 ''four-week'':173 ''github.com'':333 ''github.com/jeffsackmann/tennis_atp)'':332 ''govern'':235 ''grand'':109,237 ''howev'':160 ''individu'':241,295 ''instead'':147 ''intern'':150,213 ''ioc'':153,298 ''itf'':59,128,146,176,216,245,312,325 ''januari'':21 ''jeff'':330 ''joint'':210 ''known'':14 ''level'':97,127 ''master'':79,258 ''men'':35,60,313 ''money'':229 ''number'':226 ''olymp'':117,151,156,171,292 ''organ'':36 ''organis'':69 ''overse'':90 ''overseen'':143 ''play'':197 ''player'':183 ''point'':163,191,234 ''portion'':114 ''prize'':228 ''profession'':42,221 ''purview'':137 ''rank'':3,162,190,233 ''run'':209 ''sackmann'':331 ''satellit'':177 ''season'':201 ''season-end'':200 ''second'':45 ''second-ti'':44 ''see'':240,294 ''senior'':108 ''slam'':110,238 ''small'':113 ''team'':186 ''tenni'':32,41,63,118,130,214,222 ''third'':56 ''third-tier'':55 ''tier'':31,46,57 ''top'':30 ''top-tier'':29 ''total'':227 ''tour'':2,13,19,33,47,52,64,73,76,94,101,106,131,223,301 ''tournament'':111,119,178 ''usd'':230 ''week'':175 ''winner'':231 ''wise'':6,10 ''women'':67 ''world'':18,62,129 ''worldwid'':28 ''wta'':72 ''year'':9,196 ''year-wis'':8');
INSERT INTO public.datasets VALUES (69, 'kaggle', 'noeyislearning/sales-simulation', 'Sales Simulation', 'The Sales Simulation dataset is a synthetically generated dataset designed to simulate customer purchase behavior. It includes detailed information on customer demographics, purchase details, loyalty program participation, and transaction outcomes. The dataset is ideal for analyzing customer behavior, evaluating loyalty programs, and predicting purchase patterns. It can be used for tasks such as customer segmentation, sales forecasting, and marketing strategy optimization.



## Key Features

- **Customer Demographics**: Includes age, sex, country, and contact information.

- **Purchase Details**: Product category, purchase medium, order ID, and transaction dates.

- **Loyalty Program**: Participation status, loyalty tier, and tier-based discounts.

- **Discounts and Payments**: Total discounts, payment methods, and final purchase amounts.

- **Customer Experience**: Customer experience rating for each transaction.

- **Large Dataset**: Contains multiple records for robust analysis.

- **Tabular Format**: Easy to import and process in various data analysis tools.', '{business,tabular,text,synthetic}', 'csv', 96098.75, 'active', 'https://www.kaggle.com/api/v1/datasets/download/noeyislearning/sales-simulation', 'https://www.kaggle.com/datasets/noeyislearning/sales-simulation', '2026-03-18 01:45:52.347', '''age'':69 ''amount'':107 ''analysi'':123,134 ''analyz'':38 ''base'':95 ''behavior'':17,40 ''categori'':78 ''contact'':73 ''contain'':118 ''countri'':71 ''custom'':15,23,39,56,66,108,110 ''data'':133 ''dataset'':6,11,34,117 ''date'':85 ''demograph'':24,67 ''design'':12 ''detail'':20,26,76 ''discount'':96,97,101 ''easi'':126 ''evalu'':41 ''experi'':109,111 ''featur'':65 ''final'':105 ''forecast'':59 ''format'':125 ''generat'':10 ''id'':82 ''ideal'':36 ''import'':128 ''includ'':19,68 ''inform'':21,74 ''key'':64 ''larg'':116 ''loyalti'':27,42,86,90 ''market'':61 ''medium'':80 ''method'':103 ''multipl'':119 ''optim'':63 ''order'':81 ''outcom'':32 ''particip'':29,88 ''pattern'':47 ''payment'':99,102 ''predict'':45 ''process'':130 ''product'':77 ''program'':28,43,87 ''purchas'':16,25,46,75,79,106 ''rate'':112 ''record'':120 ''robust'':122 ''sale'':1,4,58 ''segment'':57 ''sex'':70 ''simul'':2,5,14 ''status'':89 ''strategi'':62 ''synthet'':9 ''tabular'':124 ''task'':53 ''tier'':91,94 ''tier-bas'':93 ''tool'':135 ''total'':100 ''transact'':31,84,115 ''use'':51 ''various'':132');
INSERT INTO public.datasets VALUES (71, 'kaggle', 'anikets95/bmtc-gtfs-dataset', 'BMTC GTFS Dataset', '### Dataset Summary



This dataset comprises seven files, including three CSV files, three GeoJSON files, and one GTFS zip file. The data is sourced via an API hosted by BMTC under an unofficial capacity, and while it may contain inaccuracies, it has been validated against GTFS standards. Currently, efforts are underway to update this data on a weekly (or daily) basis.



For more information on the development process, you can track the project on GitHub: [Development Repository](https://github.com/anikets95/bmtc-gtfs) and [Data Repository](https://github.com/anikets95/bmtc-data)



Additional Links:

- [BMTC Web Portal](https://bmtcwebportal.amnex.com/)

- [GTFS Standards](https://gtfs.org/)



Please refer to these links for further details on the BMTC API and GTFS standards.', '{india,transportation,intermediate,tabular,english}', 'csv', 77399.68, 'active', 'https://www.kaggle.com/api/v1/datasets/download/anikets95/bmtc-gtfs-dataset', 'https://www.kaggle.com/datasets/anikets95/bmtc-gtfs-dataset', '2026-03-17 05:45:27.88', '''/)'':96,101 ''/anikets95/bmtc-data)'':88 ''/anikets95/bmtc-gtfs)'':82 ''addit'':89 ''api'':29,113 ''basi'':63 ''bmtc'':1,32,91,112 ''bmtcwebportal.amnex.com'':95 ''bmtcwebportal.amnex.com/)'':94 ''capac'':36 ''compris'':8 ''contain'':41 ''csv'':13 ''current'':50 ''daili'':62 ''data'':24,57,84 ''dataset'':3,4,7 ''detail'':109 ''develop'':69,78 ''effort'':51 ''file'':10,14,17,22 ''geojson'':16 ''github'':77 ''github.com'':81,87 ''github.com/anikets95/bmtc-data)'':86 ''github.com/anikets95/bmtc-gtfs)'':80 ''gtfs'':2,20,48,97,115 ''gtfs.org'':100 ''gtfs.org/)'':99 ''host'':30 ''inaccuraci'':42 ''includ'':11 ''inform'':66 ''link'':90,106 ''may'':40 ''one'':19 ''pleas'':102 ''portal'':93 ''process'':70 ''project'':75 ''refer'':103 ''repositori'':79,85 ''seven'':9 ''sourc'':26 ''standard'':49,98,116 ''summari'':5 ''three'':12,15 ''track'':73 ''underway'':53 ''unoffici'':35 ''updat'':55 ''valid'':46 ''via'':27 ''web'':92 ''week'':60 ''zip'':21');
INSERT INTO public.datasets VALUES (72, 'kaggle', 'jamesb7/fuel-prices-uk', 'fuel-prices-uk', '

## About This Dataset

This dataset provides real-time and historical UK retail fuel prices at an individual forecourt level, sourced directly from the UK Government''s official [Fuel Finder API](https://www.gov.uk/guidance/access-fuel-price-data) тАФ the same open data standard mandated for all major fuel retailers operating in Great Britain.

Data is collected and published via **[fuelcosts.co.uk](https://fuelcosts.co.uk)**, a UK fuel price comparison platform aggregating prices from over 8,000 petrol stations across England, Scotland, and Wales.

---

## What''s Included

Each record represents a single fuel price at a specific station at a point in time, and includes:

- **Station metadata** тАФ name, brand, address, postcode, latitude/longitude
- **Fuel types** тАФ unleaded petrol (E10), diesel (B7), super unleaded, premium diesel
- **Price** тАФ in pence per litre (PPL)
- **Timestamp** тАФ when the price was last reported by the retailer

Retailers currently covered include BP, Shell, Esso, Jet, Texaco, Morrisons, Asda, Sainsbury''s, Tesco, Co-op, and many independent forecourts.

---

## Potential Use Cases

- **Price trend analysis** тАФ track how pump prices respond to crude oil movements, seasonal demand, or government duty changes
- **Regional price mapping** тАФ identify geographic disparities between urban and rural areas, or across UK regions
- **Retailer benchmarking** тАФ compare pricing strategies across supermarket vs. branded vs. independent forecourts
- **Cost of living research** тАФ fuel prices as an input to wider economic analysis
- **Route and travel planning models** тАФ build optimisation tools that factor in fuel cost by location
- **Forecasting** тАФ train predictive models on price movement over time

---

## Data Source & Methodology

Prices are sourced from the UK Government''s Fuel Finder open data initiative, which requires all fuel retailers to publish live pump prices in a standardised JSON format. Data is pulled at regular intervals and stored with timestamps to build a historical record.

This means prices reflect **retailer-reported data**, updated as frequently as retailers push changes to their feeds тАФ typically within hours of a forecourt price change.

---

## Coverage

| Attribute | Detail |
|---|---|
| Geography | Great Britain (England, Scotland, Wales) |
| Stations | 8,000+ |
| Update frequency | Daily |
| Fuel types | E10, B7, super unleaded, premium diesel |
| Format | CSV / JSON |

---

## License & Attribution

Underlying price data is published under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Dataset compiled and maintained by [fuelcosts.co.uk](https://fuelcosts.co.uk).
', '{government,economics,"automobiles and vehicles",tabular,"oil and gas"}', 'csv', 38230.69, 'active', 'https://www.kaggle.com/api/v1/datasets/download/jamesb7/fuel-prices-uk', 'https://www.kaggle.com/datasets/jamesb7/fuel-prices-uk', '2026-03-22 23:30:06.957', '''/doc/open-government-licence/version/3/).'':355 ''/guidance/access-fuel-price-data)'':38 ''000'':73,325 ''8'':72,324 ''across'':76,190,198 ''address'':106 ''aggreg'':68 ''analysi'':162,217 ''api'':35 ''area'':188 ''asda'':146 ''attribut'':315,341 ''b7'':115,332 ''benchmark'':194 ''bp'':140 ''brand'':105,201 ''britain'':53,319 ''build'':223,284 ''case'':159 ''chang'':177,302,313 ''co'':151 ''co-op'':150 ''collect'':56 ''compar'':195 ''comparison'':66 ''compil'':357 ''cost'':205,230 ''cover'':138 ''coverag'':314 ''crude'':169 ''csv'':338 ''current'':137 ''daili'':328 ''data'':42,54,242,256,273,295,344 ''dataset'':7,9,356 ''demand'':173 ''detail'':316 ''diesel'':114,119,336 ''direct'':26 ''dispar'':183 ''duti'':176 ''e10'':113,331 ''econom'':216 ''england'':77,320 ''esso'':142 ''factor'':227 ''feed'':305 ''finder'':34,254 ''forecast'':233 ''forecourt'':23,156,204,311 ''format'':272,337 ''frequenc'':327 ''frequent'':298 ''fuel'':2,18,33,48,64,89,109,209,229,253,261,329 ''fuel-prices-uk'':1 ''fuelcosts.co.uk'':60,61,361,362 ''geograph'':182 ''geographi'':317 ''govern'':30,175,251,350 ''great'':52,318 ''histor'':15,286 ''hour'':308 ''identifi'':181 ''includ'':83,101,139 ''independ'':155,203 ''individu'':22 ''initi'':257 ''input'':213 ''interv'':278 ''jet'':143 ''json'':271,339 ''last'':131 ''latitude/longitude'':108 ''level'':24 ''licenc'':351 ''licens'':340 ''litr'':124 ''live'':207,265 ''locat'':232 ''maintain'':359 ''major'':47 ''mandat'':44 ''mani'':154 ''map'':180 ''mean'':289 ''metadata'':103 ''methodolog'':244 ''model'':222,236 ''morrison'':145 ''movement'':171,239 ''name'':104 ''offici'':32 ''oil'':170 ''op'':152 ''open'':41,255,349 ''oper'':50 ''optimis'':224 ''penc'':122 ''per'':123 ''petrol'':74,112 ''plan'':221 ''platform'':67 ''point'':97 ''postcod'':107 ''potenti'':157 ''ppl'':125 ''predict'':235 ''premium'':118,335 ''price'':3,19,65,69,90,120,129,160,166,179,196,210,238,245,267,290,312,343 ''provid'':10 ''publish'':58,264,346 ''pull'':275 ''pump'':165,266 ''push'':301 ''real'':12 ''real-tim'':11 ''record'':85,287 ''reflect'':291 ''region'':178,192 ''regular'':277 ''report'':132,294 ''repres'':86 ''requir'':259 ''research'':208 ''respond'':167 ''retail'':17,49,135,136,193,262,293,300 ''retailer-report'':292 ''rout'':218 ''rural'':187 ''sainsburi'':147 ''scotland'':78,321 ''season'':172 ''shell'':141 ''singl'':88 ''sourc'':25,243,247 ''specif'':93 ''standard'':43 ''standardis'':270 ''station'':75,94,102,323 ''store'':280 ''strategi'':197 ''super'':116,333 ''supermarket'':199 ''tesco'':149 ''texaco'':144 ''time'':13,99,241 ''timestamp'':126,282 ''tool'':225 ''track'':163 ''train'':234 ''travel'':220 ''trend'':161 ''type'':110,330 ''typic'':306 ''uk'':4,16,29,63,191,250 ''under'':342 ''unlead'':111,117,334 ''updat'':296,326 ''urban'':185 ''use'':158 ''v3.0'':352 ''via'':59 ''vs'':200,202 ''wale'':80,322 ''wider'':215 ''within'':307 ''www.gov.uk'':37 ''www.gov.uk/guidance/access-fuel-price-data)'':36 ''www.nationalarchives.gov.uk'':354 ''www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).'':353');
INSERT INTO public.datasets VALUES (73, 'kaggle', 'kalilurrahman/new-york-times-covid19-dataset', 'New York Times - COVID-19 Dataset', '### Context

New York Times COVID Dataset from 
[https://www.github.com/nytimes/covid-19-data/](https://www.github.com/nytimes/covid-19-data/)

### Content

Provides data at the state and county level

### Acknowledgements

From NYT Github site', '{"exploratory data analysis","data visualization",tabular,news,covid19,plotly}', 'csv', 112073.56, 'active', 'https://www.kaggle.com/api/v1/datasets/download/kalilurrahman/new-york-times-covid19-dataset', 'https://www.kaggle.com/datasets/kalilurrahman/new-york-times-covid19-dataset', '2026-03-23 11:57:19.98', '''-19'':5 ''/nytimes/covid-19-data/](https://www.github.com/nytimes/covid-19-data/)'':16 ''acknowledg'':26 ''content'':17 ''context'':7 ''counti'':24 ''covid'':4,11 ''data'':19 ''dataset'':6,12 ''github'':29 ''level'':25 ''new'':1,8 ''nyt'':28 ''provid'':18 ''site'':30 ''state'':22 ''time'':3,10 ''www.github.com'':15 ''www.github.com/nytimes/covid-19-data/](https://www.github.com/nytimes/covid-19-data/)'':14 ''york'':2,9');
INSERT INTO public.datasets VALUES (77, 'kaggle', 'kimminh21/job-postings', 'Indeed Job Postings Index', 'The dataset is taken from Indeed''s Hiring Lab about the amount of job postings on their platform. It uses a special index, set as 100 on Feb 1, 2020 and change by percentage from that point.

There are currently 7 countries included in this dataset: Australia, Canada, Germany, France, the UK, Ireland and the US. ', '{tabular,"jobs and career"}', 'csv', 128503.81, 'active', 'https://www.kaggle.com/api/v1/datasets/download/kimminh21/job-postings', 'https://www.kaggle.com/datasets/kimminh21/job-postings', '2026-03-03 21:26:58.913', '''1'':33 ''100'':30 ''2020'':34 ''7'':45 ''amount'':16 ''australia'':51 ''canada'':52 ''chang'':36 ''countri'':46 ''current'':44 ''dataset'':6,50 ''feb'':32 ''franc'':54 ''germani'':53 ''hire'':12 ''includ'':47 ''inde'':1,10 ''index'':4,27 ''ireland'':57 ''job'':2,18 ''lab'':13 ''percentag'':38 ''platform'':22 ''point'':41 ''post'':3,19 ''set'':28 ''special'':26 ''taken'':8 ''uk'':56 ''us'':60 ''use'':24');
INSERT INTO public.datasets VALUES (78, 'kaggle', 'jtrotman/formula-1-race-events', 'Formula 1 Race Events', 'This dataset complements the [existing ergast.com F1 dataset](https://www.kaggle.com/jtrotman/formula-1-race-data) with *events* that happened in Grand Prix, currently:
- red flags
- safety car deployments
- virtual safety car deployments

Data is collected from these pages:

- https://en.wikipedia.org/wiki/Safety_car#List_of_safety_car_deployments_in_Formula_One_races
- https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races

Example usage in F1 Race Traces notebooks: [2025](https://www.kaggle.com/code/jtrotman/f1-race-traces-2025).
', '{"auto racing",sports,history,tabular}', 'json', 39.79, 'active', 'https://www.kaggle.com/api/v1/datasets/download/jtrotman/formula-1-race-events', 'https://www.kaggle.com/datasets/jtrotman/formula-1-race-events', '2026-03-15 11:50:25.11', '''/code/jtrotman/f1-race-traces-2025).'':55 ''/jtrotman/formula-1-race-data)'':15 ''/wiki/list_of_red-flagged_formula_one_races'':44 ''/wiki/safety_car#list_of_safety_car_deployments_in_formula_one_races'':41 ''1'':2 ''2025'':52 ''car'':27,31 ''collect'':35 ''complement'':7 ''current'':23 ''data'':33 ''dataset'':6,12 ''deploy'':28,32 ''en.wikipedia.org'':40,43 ''en.wikipedia.org/wiki/list_of_red-flagged_formula_one_races'':42 ''en.wikipedia.org/wiki/safety_car#list_of_safety_car_deployments_in_formula_one_races'':39 ''ergast.com'':10 ''event'':4,17 ''exampl'':45 ''exist'':9 ''f1'':11,48 ''flag'':25 ''formula'':1 ''grand'':21 ''happen'':19 ''notebook'':51 ''page'':38 ''prix'':22 ''race'':3,49 ''red'':24 ''safeti'':26,30 ''trace'':50 ''usag'':46 ''virtual'':29 ''www.kaggle.com'':14,54 ''www.kaggle.com/code/jtrotman/f1-race-traces-2025).'':53 ''www.kaggle.com/jtrotman/formula-1-race-data)'':13');
INSERT INTO public.datasets VALUES (79, 'kaggle', 'aravindram11/jeopardy-dataset-updated', 'Jeopardy Dataset (Updated)', 'Here is a json file containing 216,930 Jeopardy questions, answers and other data.

The json file is an unordered list of questions where each question has

''category'' : the question category, e.g. "HISTORY"
''value'' : $ value of the question as string, e.g. "$200"
''question'' : text of question
''answer'' : text of answer
''round'' : one of "Jeopardy!","Double Jeopardy!","Final Jeopardy!" or "Tiebreaker"
''show_number'' : string of show number, e.g ''4680''
''air_date'' : the show air date in format YYYY-MM-DD
', '{tabular,json}', 'json', 54252.56, 'active', 'https://www.kaggle.com/api/v1/datasets/download/aravindram11/jeopardy-dataset-updated', 'https://www.kaggle.com/datasets/aravindram11/jeopardy-dataset-updated', '2022-06-11 23:48:24.527', '''200'':45 ''216'':10 ''4680'':71 ''930'':11 ''air'':72,76 ''answer'':14,50,53 ''categori'':31,34 ''contain'':9 ''data'':17 ''dataset'':2 ''date'':73,77 ''dd'':83 ''doubl'':58 ''e.g'':35,44,70 ''file'':8,20 ''final'':60 ''format'':79 ''histori'':36 ''jeopardi'':1,12,57,59,61 ''json'':7,19 ''list'':24 ''mm'':82 ''number'':65,69 ''one'':55 ''question'':13,26,29,33,41,46,49 ''round'':54 ''show'':64,68,75 ''string'':43,66 ''text'':47,51 ''tiebreak'':63 ''unord'':23 ''updat'':3 ''valu'':37,38 ''yyyi'':81 ''yyyy-mm-dd'':80');
INSERT INTO public.datasets VALUES (10, 'kaggle', 'odins0n/top-20-play-store-app-reviews-daily-update', 'Top 20 Play Store App Reviews (Daily Update) ', 'The Dataset consists of **10000** latest reviews from the **Top 20** apps on the Google Play Store. 
The Top 20 apps include the following:

1.  **Facebook**
2.  **WhatsApp**
3.  **Facebook Messenger**
4. **Instagram**
5. **TikTok**
6. **Subway Surfers**
7. **Facebook Lite**
8. **Microsoft Word**
9. **Microsoft PowerPoint**
10. **Snapchat**
11. **SHAREit**
12. **Netflix**
13. **Twitter**
14. **Flipboard**
15. **Candy Crush Saga**
16. **Skype**
17.  **Spotify**
18. **Dropbox**
19. **Viber**
20. **LINE**', '{"mobile and wireless",tabular,text,"multiclass classification"}', 'csv', 40332.55, 'active', 'https://www.kaggle.com/api/v1/datasets/download/odins0n/top-20-play-store-app-reviews-daily-update', 'https://www.kaggle.com/datasets/odins0n/top-20-play-store-app-reviews-daily-update', '2026-03-23 01:34:12.237', '''1'':33 ''10'':56 ''10000'':13 ''11'':58 ''12'':60 ''13'':62 ''14'':64 ''15'':66 ''16'':70 ''17'':72 ''18'':74 ''19'':76 ''2'':35 ''20'':2,19,28,78 ''3'':37 ''4'':40 ''5'':42 ''6'':44 ''7'':47 ''8'':50 ''9'':53 ''app'':5,20,29 ''candi'':67 ''consist'':11 ''crush'':68 ''daili'':7 ''dataset'':10 ''dropbox'':75 ''facebook'':34,38,48 ''flipboard'':65 ''follow'':32 ''googl'':23 ''includ'':30 ''instagram'':41 ''latest'':14 ''line'':79 ''lite'':49 ''messeng'':39 ''microsoft'':51,54 ''netflix'':61 ''play'':3,24 ''powerpoint'':55 ''review'':6,15 ''saga'':69 ''shareit'':59 ''skype'':71 ''snapchat'':57 ''spotifi'':73 ''store'':4,25 ''subway'':45 ''surfer'':46 ''tiktok'':43 ''top'':1,18,27 ''twitter'':63 ''updat'':8 ''viber'':77 ''whatsapp'':36 ''word'':52');
INSERT INTO public.datasets VALUES (14, 'kaggle', 'bwandowando/reddit-rcambodia-subreddit-dataset-2026', 'ЁЯЗ░ЁЯЗн Reddit r/Cambodia Subreddit Dataset 2026', '## Context 
I''ve tried looking for an [r/Cambodia/](https://www.reddit.com/r/Cambodia/) dataset here in Kaggle havent found one, so I made one for the Cambodian Kaggle members

## About![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1842206%2Fee78c8ea3d4979dd6378a690d24a4de5%2F_8e1c5335-c32f-40ea-8fe5-1a6a7b7243ac.jpeg?generation=1767530680407354&alt=media)

Created last Mar 03, 2010, [r/Cambodia/](https://www.reddit.com/r/Cambodia/) is labeled "**Cambodia: All about the Kingdom of Wonder.**" and has 239K members.

This dataset can be used to extract insights from the trending topics and discussions in the subreddit.

## Banner Image
Created with Bing Image Creator', '{research,internet,tabular,"online communities","social networks"}', 'csv', 895328.91, 'active', 'https://www.kaggle.com/api/v1/datasets/download/bwandowando/reddit-rcambodia-subreddit-dataset-2026', 'https://www.kaggle.com/datasets/bwandowando/reddit-rcambodia-subreddit-dataset-2026', '2026-03-23 01:39:11.65', '''/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2fee78c8ea3d4979dd6378a690d24a4de5%2f_8e1c5335-c32f-40ea-8fe5-1a6a7b7243ac.jpeg?generation=1767530680407354&alt=media)'':36 ''/r/cambodia/)'':16,45 ''03'':40 ''2010'':41 ''2026'':5 ''239k'':57 ''banner'':76 ''bing'':80 ''cambodia'':48 ''cambodian'':30 ''context'':6 ''creat'':37,78 ''creator'':82 ''dataset'':4,17,60 ''discuss'':72 ''extract'':65 ''found'':22 ''havent'':21 ''imag'':77,81 ''insight'':66 ''kaggl'':20,31 ''kingdom'':52 ''label'':47 ''last'':38 ''look'':10 ''made'':26 ''mar'':39 ''member'':32,58 ''one'':23,27 ''r/cambodia'':2,13,42 ''reddit'':1 ''subreddit'':3,75 ''topic'':70 ''trend'':69 ''tri'':9 ''use'':63 ''ve'':8 ''wonder'':54 ''www.googleapis.com'':35 ''www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2fee78c8ea3d4979dd6378a690d24a4de5%2f_8e1c5335-c32f-40ea-8fe5-1a6a7b7243ac.jpeg?generation=1767530680407354&alt=media)'':34 ''www.reddit.com'':15,44 ''www.reddit.com/r/cambodia/)'':14,43');
INSERT INTO public.datasets VALUES (74, 'kaggle', 'bwandowando/reddit-rsingapore-subreddit-dataset-2026', 'ЁЯЗ╕ЁЯЗм Reddit r/Singapore Subreddit Dataset 2026', '## Context
I''ve tried looking for an [r/Singapore/](https://www.reddit.com/r/Singapore/) dataset here in Kaggle havent found one, so I made one for the Singapore Kaggle members

## About
![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1842206%2F32f7872b6956941f063e6737a67d2403%2F_ea591f49-5fc3-4d86-833c-8936e52293ce.jpeg?generation=1767519347997680&alt=media)

Created last Jan 26, 2008, [r/Singapore/](https://www.reddit.com/r/Singapore/) is labeled Welcome to /r/singapore: The place for anything Singapore and has 1.5M members

This dataset can be used to extract insights from the trending topics and discussions in the subreddit.

## Banner Image
Created with Bing Image Creator', '{research,internet,tabular,"online communities","social networks"}', 'csv', 534510.51, 'active', 'https://www.kaggle.com/api/v1/datasets/download/bwandowando/reddit-rsingapore-subreddit-dataset-2026', 'https://www.kaggle.com/datasets/bwandowando/reddit-rsingapore-subreddit-dataset-2026', '2026-03-23 01:25:41.74', '''/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2f32f7872b6956941f063e6737a67d2403%2f_ea591f49-5fc3-4d86-833c-8936e52293ce.jpeg?generation=1767519347997680&alt=media)'':36 ''/r/singapore'':50 ''/r/singapore/)'':16,45 ''1.5'':58 ''2008'':41 ''2026'':5 ''26'':40 ''anyth'':54 ''banner'':78 ''bing'':82 ''context'':6 ''creat'':37,80 ''creator'':84 ''dataset'':4,17,62 ''discuss'':74 ''extract'':67 ''found'':22 ''havent'':21 ''imag'':79,83 ''insight'':68 ''jan'':39 ''kaggl'':20,31 ''label'':47 ''last'':38 ''look'':10 ''m'':59 ''made'':26 ''member'':32,60 ''one'':23,27 ''place'':52 ''r/singapore'':2,13,42 ''reddit'':1 ''singapor'':30,55 ''subreddit'':3,77 ''topic'':72 ''trend'':71 ''tri'':9 ''use'':65 ''ve'':8 ''welcom'':48 ''www.googleapis.com'':35 ''www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2f32f7872b6956941f063e6737a67d2403%2f_ea591f49-5fc3-4d86-833c-8936e52293ce.jpeg?generation=1767519347997680&alt=media)'':34 ''www.reddit.com'':15,44 ''www.reddit.com/r/singapore/)'':14,43');
INSERT INTO public.datasets VALUES (75, 'kaggle', 'bwandowando/reddit-raustralia-subreddit-dataset-2026', 'ЁЯЗжЁЯЗ║ Reddit r/Australia Subreddit Dataset 2026', '## Context
I''ve tried looking for an [r/Australia/](https://www.reddit.com/r/Australia/) dataset here in Kaggle havent found one, so I made one for the Australian Kaggle members

## About
![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1842206%2Fefd7073169eead0b00e9eeeba334d7c0%2F_7e80eb14-236d-41ec-bad5-861f24c333df.jpeg?generation=1767513499471165&alt=media)

Created last Jan 26, 2008, [r/Australia/](https://www.reddit.com/r/Australia/) has 2.2M members and is labeled as 

&gt;A dusty corner on the internet where you can chew the fat about Australia and Australians.

This dataset can be used to extract insights from the trending topics and discussions in the subreddit.

## Images in Dataset
![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1842206%2Ff71b0b4677cf8a5d34b288c6df92772b%2F205bd8ed-475c-511e-bd59-f6dee5ed1e3djfz7z7kbv5yd1.jpg?generation=1731805824510675&alt=media)
* (thread_id)!!(image_name).(file_extension)
* **The GUID  value in the filename is the threadid**

## Banner Image
Created with Bing Image Creator', '{research,internet,tabular,"online communities","social networks"}', 'csv', 537506.91, 'active', 'https://www.kaggle.com/api/v1/datasets/download/bwandowando/reddit-raustralia-subreddit-dataset-2026', 'https://www.kaggle.com/datasets/bwandowando/reddit-raustralia-subreddit-dataset-2026', '2026-03-23 01:05:58.83', '''/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2fefd7073169eead0b00e9eeeba334d7c0%2f_7e80eb14-236d-41ec-bad5-861f24c333df.jpeg?generation=1767513499471165&alt=media)'':36 ''/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2ff71b0b4677cf8a5d34b288c6df92772b%2f205bd8ed-475c-511e-bd59-f6dee5ed1e3djfz7z7kbv5yd1.jpg?generation=1731805824510675&alt=media)'':92 ''/r/australia/)'':16,45 ''2.2'':47 ''2008'':41 ''2026'':5 ''26'':40 ''australia'':67 ''australian'':30,69 ''banner'':108 ''bing'':112 ''chew'':63 ''context'':6 ''corner'':56 ''creat'':37,110 ''creator'':114 ''dataset'':4,17,71,89 ''discuss'':83 ''dusti'':55 ''extens'':98 ''extract'':76 ''fat'':65 ''file'':97 ''filenam'':104 ''found'':22 ''guid'':100 ''havent'':21 ''id'':94 ''imag'':87,95,109,113 ''insight'':77 ''internet'':59 ''jan'':39 ''kaggl'':20,31 ''label'':52 ''last'':38 ''look'':10 ''m'':48 ''made'':26 ''member'':32,49 ''name'':96 ''one'':23,27 ''r/australia'':2,13,42 ''reddit'':1 ''subreddit'':3,86 ''thread'':93 ''threadid'':107 ''topic'':81 ''trend'':80 ''tri'':9 ''use'':74 ''valu'':101 ''ve'':8 ''www.googleapis.com'':35,91 ''www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2fefd7073169eead0b00e9eeeba334d7c0%2f_7e80eb14-236d-41ec-bad5-861f24c333df.jpeg?generation=1767513499471165&alt=media)'':34 ''www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2f1842206%2ff71b0b4677cf8a5d34b288c6df92772b%2f205bd8ed-475c-511e-bd59-f6dee5ed1e3djfz7z7kbv5yd1.jpg?generation=1731805824510675&alt=media)'':90 ''www.reddit.com'':15,44 ''www.reddit.com/r/australia/)'':14,43');
INSERT INTO public.datasets VALUES (76, 'kaggle', 'svendaj/sec-edgar-cik-files-dataset', 'SEC EDGAR CIK Files Dataset', 'This dataset contains three basic datafiles provided by [**U.S. Securities and Exchange Commission (SEC)**](https://www.sec.gov/) containing unique identification of all regulated entities. SEC is maintaining [**Electronic Data Gathering, Analysis, and Retrieval (EDGAR)**](https://www.sec.gov/search-filings) system to access all available filings. EDGAR assigns to filers a unique numerical identifier, known as a **Central Index Key (CIK)**, when they sign up to make filings to the SEC. CIK numbers remain unique to the filer; they are not recycled.

CIK is widely used to to identify filing entity, which may be physical or legal person. To simplify association between CIK, filer name, ticker or exchange where security is traded, [EDGAR offers data files](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) to enable various searches. Unfortunately format of these data files is not consistent:
* **CIK_company_lookup.txt** text file containing name of entity and CIK separated by `:` (colon)
* **CIK_company_ticker_exchange.json** JSON file containing names of publicly traded companies with their CIK, ticker and stock exchange where this ticker is trading
* **mutual_funds_CIK_series_class_ticker.json** JSON file containing mutual fund CIK, their Series ID, Class ID and trading symbol of the mutual fund

These datafiles are weekly downloaded directly from EDGAR and translated them into popular `csv` and `parquet` formats.

CIK is always the number but sometimes it is used as 10 digits long number with leading zeros. This dataset is always treating CIK as `int`, so if you would need 10 digits long format you can translate it in Python by `str(CIK).zfill(10)`.', '{"united states",government,economics,beginner,tabular}', 'csv', 93978.06, 'active', 'https://www.kaggle.com/api/v1/datasets/download/svendaj/sec-edgar-cik-files-dataset', 'https://www.kaggle.com/datasets/svendaj/sec-edgar-cik-files-dataset', '2026-03-22 16:32:48.357', '''/)'':22 ''/search-filings)'':42 ''/search-filings/edgar-search-assistance/accessing-edgar-data)'':121 ''10'':215,235,249 ''access'':45 ''alway'':206,225 ''analysi'':36 ''assign'':50 ''associ'':103 ''avail'':47 ''basic'':10 ''central'':60 ''cik'':3,63,74,85,105,143,158,174,204,227,247 ''cik_company_lookup.txt'':135 ''cik_company_ticker_exchange.json'':147 ''class'':178 ''colon'':146 ''commiss'':18 ''compani'':155 ''consist'':134 ''contain'':8,23,138,150,171 ''csv'':200 ''data'':34,117,130 ''datafil'':11,188 ''dataset'':5,7,223 ''digit'':216,236 ''direct'':192 ''download'':191 ''edgar'':2,39,49,115,194 ''electron'':33 ''enabl'':123 ''entiti'':29,93,141 ''exchang'':17,110,162 ''file'':4,48,70,92,118,131,137,149,170 ''filer'':52,80,106 ''format'':127,203,238 ''fund'':173,186 ''gather'':35 ''id'':177,179 ''identif'':25 ''identifi'':56,91 ''index'':61 ''int'':229 ''json'':148,169 ''key'':62 ''known'':57 ''lead'':220 ''legal'':99 ''long'':217,237 ''maintain'':32 ''make'':69 ''may'':95 ''mutual'':172,185 ''mutual_funds_cik_series_class_ticker.json'':168 ''name'':107,139,151 ''need'':234 ''number'':75,208,218 ''numer'':55 ''offer'':116 ''parquet'':202 ''person'':100 ''physic'':97 ''popular'':199 ''provid'':12 ''public'':153 ''python'':244 ''recycl'':84 ''regul'':28 ''remain'':76 ''retriev'':38 ''search'':125 ''sec'':1,19,30,73 ''secur'':15,112 ''separ'':144 ''seri'':176 ''sign'':66 ''simplifi'':102 ''sometim'':210 ''stock'':161 ''str'':246 ''symbol'':182 ''system'':43 ''text'':136 ''three'':9 ''ticker'':108,159,165 ''trade'':114,154,167,181 ''translat'':196,241 ''treat'':226 ''u.s'':14 ''unfortun'':126 ''uniqu'':24,54,77 ''use'':88,213 ''various'':124 ''week'':190 ''wide'':87 ''would'':233 ''www.sec.gov'':21,41,120 ''www.sec.gov/)'':20 ''www.sec.gov/search-filings)'':40 ''www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)'':119 ''zero'':221 ''zfill'':248');
INSERT INTO public.datasets VALUES (81, 'kaggle', 'niteshkakkar/clash-royal-cards-data', 'Clash Royale Cards Data', 'This dataset provides a comprehensive view of all Clash Royale cards, combining core gameplay attributes with usage and balance-related statistics. Each entry represents a card and includes details such as elixir cost, rarity, evolution levels, mobility, and attack type. The dataset also includes derived fields like hitpoints and usage frequency, allowing for strategic and analytical insights into the gameтАЩs meta.

It can be used for various types of analysis from studying the relationship between card cost and effectiveness to exploring balance trends across rarities and troop types. Developers and data analysts can also apply this data in visualization projects, AI-driven strategy tools, or game balance simulations.

All original game data and images belong to Supercell. This dataset is a structured aggregation created for research, learning, and non-commercial analytical purposes.', '{games,tabular,english}', 'json', 80.99, 'active', 'https://www.kaggle.com/api/v1/datasets/download/niteshkakkar/clash-royal-cards-data', 'https://www.kaggle.com/datasets/niteshkakkar/clash-royal-cards-data', '2025-10-30 06:09:20.8', '''across'':90 ''aggreg'':130 ''ai'':108 ''ai-driven'':107 ''allow'':57 ''also'':48,100 ''analysi'':76 ''analyst'':98 ''analyt'':61,139 ''appli'':101 ''attack'':44 ''attribut'':19 ''balanc'':24,88,114 ''balance-rel'':23 ''belong'':122 ''card'':3,15,31,82 ''clash'':1,13 ''combin'':16 ''commerci'':138 ''comprehens'':9 ''core'':17 ''cost'':38,83 ''creat'':131 ''data'':4,97,103,119 ''dataset'':6,47,126 ''deriv'':50 ''detail'':34 ''develop'':95 ''driven'':109 ''effect'':85 ''elixir'':37 ''entri'':28 ''evolut'':40 ''explor'':87 ''field'':51 ''frequenc'':56 ''game'':65,113,118 ''gameplay'':18 ''hitpoint'':53 ''imag'':121 ''includ'':33,49 ''insight'':62 ''learn'':134 ''level'':41 ''like'':52 ''meta'':67 ''mobil'':42 ''non'':137 ''non-commerci'':136 ''origin'':117 ''project'':106 ''provid'':7 ''purpos'':140 ''rariti'':39,91 ''relat'':25 ''relationship'':80 ''repres'':29 ''research'':133 ''royal'':2,14 ''simul'':115 ''statist'':26 ''strateg'':59 ''strategi'':110 ''structur'':129 ''studi'':78 ''supercel'':124 ''tool'':111 ''trend'':89 ''troop'':93 ''type'':45,74,94 ''usag'':21,55 ''use'':71 ''various'':73 ''view'':10 ''visual'':105');
INSERT INTO public.datasets VALUES (82, 'kaggle', 'mpwolke/mbppjsonl', 'MBPP Python Problems jsonl', 'CITATION = 
@article{austin2021program,
  title={Program Synthesis with Large Language Models},
  author={Austin, Jacob and Odena, Augustus and Nye, Maxwell and Bosma, Maarten and Michalewski, Henryk and Dohan, David and Jiang, Ellen and Cai, Carrie and Terry, Michael and Le, Quoc and others},
  journal={arXiv preprint arXiv:2108.07732},
  year={2021}
}


"The MBPP (Mostly Basic Python Problems) dataset consists of around 1,000 crowd-sourced Python
programming problems, designed to be solvable by entry level programmers, covering programming
fundamentals, standard library functionality, and so on. Each problem consists of a task
description, code solution and 3 automated test cases. "

https://github.com/google-research/google-research/blob/master/mbpp/mbpp.jsonl

', '{"computer science",programming,tabular,text}', 'json', 550.53, 'active', 'https://www.kaggle.com/api/v1/datasets/download/mpwolke/mbppjsonl', 'https://www.kaggle.com/datasets/mpwolke/mbppjsonl', '2023-12-03 18:21:48.413', '''/google-research/google-research/blob/master/mbpp/mbpp.jsonl'':105 ''000'':65 ''1'':64 ''2021'':53 ''2108.07732'':51 ''3'':99 ''around'':63 ''articl'':6 ''arxiv'':48,50 ''augustus'':20 ''austin'':16 ''austin2021program'':7 ''author'':15 ''autom'':100 ''basic'':57 ''bosma'':25 ''cai'':37 ''carri'':38 ''case'':102 ''citat'':5 ''code'':96 ''consist'':61,91 ''cover'':80 ''crowd'':67 ''crowd-sourc'':66 ''dataset'':60 ''david'':32 ''descript'':95 ''design'':72 ''dohan'':31 ''ellen'':35 ''entri'':77 ''function'':85 ''fundament'':82 ''github.com'':104 ''github.com/google-research/google-research/blob/master/mbpp/mbpp.jsonl'':103 ''henryk'':29 ''jacob'':17 ''jiang'':34 ''journal'':47 ''jsonl'':4 ''languag'':13 ''larg'':12 ''le'':43 ''level'':78 ''librari'':84 ''maarten'':26 ''maxwel'':23 ''mbpp'':1,55 ''michael'':41 ''michalewski'':28 ''model'':14 ''most'':56 ''nye'':22 ''odena'':19 ''other'':46 ''preprint'':49 ''problem'':3,59,71,90 ''program'':9,70,81 ''programm'':79 ''python'':2,58,69 ''quoc'':44 ''solut'':97 ''solvabl'':75 ''sourc'':68 ''standard'':83 ''synthesi'':10 ''task'':94 ''terri'':40 ''test'':101 ''titl'':8 ''year'':52');
COMMIT;