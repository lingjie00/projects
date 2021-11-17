library(tidyverse)

#source: https://data.gov.sg/dataset/median-rent-by-town-and-flat-type
file = "/Users/lingjie/Desktop/Projects/SIRS_HDB_eligibility/median-rent-by-town-and-flat-type/median-rent-by-town-and-flat-type.csv"

#import data and filter "na"(Data not available or not applicable) and "-"(Data is negligible or not significant)
rental = read.csv(file,stringsAsFactors=FALSE)
rental$median_rent = rental$median_rent %>% str_replace("-", "NA")
rental$median_rent = rental$median_rent %>% str_replace("na", "NA")
rental$median_rent = rental$median_rent %>% parse_number()

#filter to 2020 data
rental_2020 = rental %>% filter(str_detect(quarter,"2020-Q1"))

#investigate missing data
missing_price = rental_2020 %>% filter(is.na(median_rent)) %>% select(town,flat_type)

#get all data available
get_all_non_na_data = function(town_name,flat_kind) {
  non_na = rental %>% filter(town==town_name & flat_type==flat_kind) %>% filter(!is.na(median_rent))
  latest = non_na[nrow(non_na),] %>% rename()
  return(latest)
}
get_all_non_na_data("SERANGOON","EXEC")

missing_price_fixed = data.frame(c())

for(i in 1:nrow(missing_price)){
  town_name = missing_price[i,1]
  flat_kind = missing_price[i,2]
  data = get_all_non_na_data(town_name,flat_kind)
  if(nrow(data)==0){}
  else{
    missing_price_fixed = rbind(missing_price_fixed,data)
  }
}
rownames(missing_price_fixed) = NULL

#add only the recent 3 years data 2017:2019
missing_price_fixed_recent_index = missing_price_fixed %>% select(quarter) %>%
  sapply(function(x) str_detect(x, pattern="201[7-9]"))
missing_price_fixed_recent = missing_price_fixed[missing_price_fixed_recent_index,]
rownames(missing_price_fixed_recent) = NULL

rental_2020_fixed_na = rbind(rental_2020,missing_price_fixed_recent) %>% arrange(town,flat_type,quarter)
rownames(rental_2020_fixed_na) = NULL #reset index

#data visualisation
plot_price_by_flat_type = rental_2020 %>% filter(!median_rent=="NA") %>% 
  ggplot(aes(x=flat_type,y=median_rent,col=town)) + 
  geom_jitter() + scale_y_continuous(breaks=seq(min(rental$median_rent,na.rm=TRUE),max(rental$median_rent,na.rm=TRUE),by=200)) + 
  geom_hline(yintercept=1750) + ggtitle("Singapore rental price by flat type")

plot_price_by_town = rental_2020 %>% filter(!median_rent=="NA") %>% mutate(town = reorder(town,median_rent,FUN=mean)) %>%
  ggplot(aes(x=town,y=median_rent,col=flat_type)) + 
  geom_point(aes(shape=flat_type)) + theme(axis.text.x=element_text(angle=90,hjust=1)) +
  geom_hline(yintercept=1750) + ggtitle("Singapore rental price by town")

#filter to SIRS Eligibility, 2020 data
rental_sirs = rental_2020 %>% filter(median_rent<=1750)

plot_eligible_town = rental_sirs %>% filter(!median_rent=="NA") %>% mutate(town = reorder(town,median_rent,FUN=mean)) %>% 
  ggplot(aes(x=town,y=median_rent,col=flat_type)) + 
  geom_point(aes(shape=flat_type)) + theme(axis.text.x=element_text(angle=90,hjust=1)) + ggtitle("Town eligible for SIRS")


#report
plot_price_by_flat_type
plot_price_by_town
plot_eligible_town
