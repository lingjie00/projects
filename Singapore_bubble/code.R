##inspired by the Economist's travel bubble
##https://www.economist.com/finance-and-economics/2020/05/14/could-travel-bubbles-offer-a-route-to-economic-recovery

##Singapore trade data taken from Department of Statistics, Singapore
##https://www.singstat.gov.sg/find-data/search-by-theme?theme=trade&type=all

##Covid figure taken from Jogns Hopkins University
##Figures are taken for 17 May 2020
##https://github.com/CSSEGISandData/COVID-19/

library(tidyverse)
library(rvest)

setwd("/Users/lingjie/Desktop/git/Singapore_bubble/data")

##Import data
##covid figures
covid_data = read_csv("covid 05-16-2020.csv")
covid_data = covid_data %>% group_by(Country_Region) %>% summarize(Confirmed=sum(Confirmed), Deaths=sum(Deaths), 
                                                                   Recovered=sum(Recovered), Active=sum(Active))
covid_data = covid_data %>% mutate(Rank=rank(-Active, ties.method="min")) %>% arrange(Rank) #rank by current active cases
covid_data = rename(covid_data, Country = Country_Region)
covid_data

##Singapore trade figures
#we only select 2019 data and countries that have both export and import data with Singapore
region = c("Asia", "Europe", "America", "European Union", "ASEAN")

goods_import = read_csv("Merchandise_Imports.csv")
goods_import = goods_import %>% gather(Year, Trade, `1976 Jan`:`2020 Mar`, convert=TRUE) %>% separate(Year, c("Year", "Month"))
goods_import = goods_import %>% mutate(Year = str_remove(goods_import$Year, 'X')) %>% 
  mutate(Variables = trimws(Variables), Trade=parse_number(str_trim(Trade))) %>%
  separate(Variables, c("Country", "Units"), sep="\\([TM]", extra="merge") %>% filter(!str_detect(Country, "Total")) %>%
  mutate(Trade = ifelse(Units=="illion Dollars)", Trade*1000000, Trade*1000)) %>% select(-Units) %>%
  group_by(Country, Year) %>% summarize(Trade=sum(Trade)) %>% filter(Year==2019) %>% as_tibble()
goods_import = goods_import %>% mutate(Country=trimws(Country)) %>% filter( (!Country%in%region) & (!Trade==0)) %>% 
  mutate(Rank=rank(-Trade, ties.method="min")) %>% arrange(Rank)

goods_export = read_csv("Merchandise_Exports.csv")
goods_export = goods_export %>% gather(Year, Trade, `1976 Jan`:`2020 Mar`, convert=TRUE) %>% separate(Year, c("Year", "Month"))
goods_export = goods_export %>% mutate(Variables = trimws(Variables), Trade=parse_number(str_trim(Trade))) %>%
  separate(Variables, c("Country", "Units"), sep="\\([TM]", extra="merge") %>% filter(!str_detect(Country, "Total")) %>%
  mutate(Trade = ifelse(Units=="illion Dollars)", Trade*1000000, Trade*1000)) %>% select(-Units) %>%
  group_by(Country, Year) %>% summarize(Trade=sum(Trade)) %>% filter(Year==2019) %>% as_tibble()
goods_export = goods_export %>% mutate(Country=trimws(Country)) %>% filter( (!Country%in%region) & (!Trade==0)) %>% 
  mutate(Rank=rank(-Trade, ties.method="min")) %>% arrange(Rank)

trade_data = inner_join(goods_export, goods_import, by="Country", suffix=c("_export", "_import")) %>% 
  select(-Year_import) %>% rename(Year = Year_export) %>% 
  mutate(Net_trade = Trade_export - Trade_import, Rank_net_trade = rank(-Net_trade)) %>%
  arrange(Rank_net_trade)
trade_data

##combine trade data with covid figures
trade_covid_data = left_join(trade_data, covid_data, by="Country") %>% select(-Rank)

covid_data$Country[which(covid_data$Country=="Taiwan*")] = "Taiwan"
covid_data$Country[which(covid_data$Country=="US")] = "United States"
covid_data$Country[which(covid_data$Country=="Vietnam")] = "Vietnam, Socialist Republic Of"
covid_data$Country[which(covid_data$Country=="China")] = "Mainland China"
covid_data$Country[which(covid_data$Country=="Burma")] = "Myanmar"
covid_data$Country[which(covid_data$Country=="Korea, South")] = "Republic Of Korea"
covid_data$Country[which(covid_data$Country=="Germany")] = "Germany, Federal Republic Of"
covid_data$Country[which(covid_data$Country=="Maldives")] = "Maldives, Republic Of"
covid_data$Country[which(covid_data$Country=="Brunei")] = "Brunei Darussalam"
covid_data$Country[which(covid_data$Country=="Laos")] = "Laos People's Democratic Republic"
covid_data$Country[which(covid_data$Country=="Iran")] = "Iran (Islamic Republic Of)"
covid_data$Country[which(covid_data$Country=="Syria")] = "Syrian Arab Republic"
covid_data$Country[which(covid_data$Country=="Czechia")] = "Czech Republic"
covid_data$Country[which(covid_data$Country=="Slovakia")] = "Slovak Republic (Slovakia)"

hk = data.frame(Country="Hong Kong",Confirmed=1052,Deaths=4,Recovered=1022,Active=26,Rank=NA)
macau = data.frame(Country="Macau",Confirmed=45,Deaths=0,Recovered=44,Active=1,Rank=NA)
guam = data.frame(Country="Guam",Confirmed=154,Deaths=5,Recovered=0,Active=149,Rank=NA)
new_caledonia = data.frame(Country="New Caledonia",Confirmed=18,Deaths=0,Recovered=18,Active=0,Rank=NA)
polynesia = data.frame(Country="French Polynesia",Confirmed=60,Deaths=0,Recovered=59,Active=1,Rank=NA)
rico = data.frame(Country="Puerto Rico",Confirmed=2589,Deaths=122,Recovered=0,Active=2467,Rank=NA)
oceania = covid_data %>% filter(Country=="Australia" | Country=="New Zealand") %>%
  summarize(Country = "Oceania", Confirmed=sum(Confirmed), Deaths=sum(Deaths), Recovered=sum(Recovered), Active=sum(Active), Rank=NA)
#using Austrlia and New Zealand for Oceania, using MFA reference: https://www.mfa.gov.sg/SINGAPORES-FOREIGN-POLICY/Countries-and-Regions/Oceania

covid_data$Country[which(covid_data$Country=="Congo (Kinshasa)")] = "Democratic Republic of the Congo"
covid_data$Country[which(covid_data$Country=="Congo (Brazzaville)")] = "Republic of the Congo"
covid_data$Country[which(covid_data$Country=="Sao Tome and Principe")] = "São Tomé and Príncipe"
covid_data$Country[which(covid_data$Country=="Western Sahara")] = "Western Sahara[4]"

african_url = "https://en.wikipedia.org/wiki/List_of_African_countries_by_population"
african_countries = read_html(african_url) %>% html_nodes("table") %>% .[[1]] %>% html_table() %>% .[2] %>% 
  rename(Country = `Country(or dependent territory)`)
africa = covid_data %>% filter(Country %in% african_countries & !(Country %in% trade_covid_data$Country) ) %>%
  summarize(Country = "Africa", Confirmed=sum(Confirmed), Deaths=sum(Deaths), Recovered=sum(Recovered), Active=sum(Active), Rank=NA)
missing_african_countries = african_countries[!with(african_countries, Country %in% covid_data$Country),]
missing_african_countries

oceania_url = "https://en.wikipedia.org/wiki/List_of_Oceanian_countries_by_population"
oceania_countries = read_html(oceania_url) %>% html_nodes("table") %>% .[[1]] %>% html_table(fill=TRUE) %>% .[2] %>% 
  rename(Country = `Country(or dependent territory)`)
oceania_countries = oceania_countries %>% separate(Country, c("Country"), sep="\\(") %>% mutate(Country = str_trim(Country))
oceania_countries = oceania_countries %>% 
  filter(!str_detect(Country,"Australia") & !str_detect(Country,"New Zealand") & !(Country %in% trade_covid_data$Country) )
missing_oceania_countries = oceania_countries[!with(oceania_countries, Country %in% covid_data$Country),]
missing_oceania_countries

#combining data and deleting temp data
covid_data = rbind(covid_data, hk, macau, guam, new_caledonia, polynesia, rico, oceania, africa)
rm(hk, macau, guam, new_caledonia, polynesia, rico, oceania, africa)
rm(african_url, oceania_url, region, african_countries, oceania_countries)

trade_covid_data = left_join(trade_data, covid_data, by="Country") %>% select(-Rank)
ranks = with(trade_covid_data, rank(-c(Active,18992), ties.method="min"))
sg_rank = tail(ranks,1)
trade_covid_data = trade_covid_data %>% mutate(Rank_covid = ranks[1:length(ranks)-1]) %>% arrange(Rank_covid)
missing_country = trade_covid_data[is.na(trade_covid_data$Active),] %>% select(Country) %>% as.data.frame()
missing_country

##getting possible travel
sg_active = covid_data %>% filter(Country=="Singapore") %>% pull(Active)
trade_covid_data = trade_covid_data %>% mutate(Potential = ifelse(Active<=sg_active,TRUE,FALSE))

##output data
write_csv(trade_covid_data, "trade_covid_data.csv", col_names=TRUE)


