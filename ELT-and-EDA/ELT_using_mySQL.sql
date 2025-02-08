CREATE DATABASE `churn_prediction`;

USE churn_prediction;

SELECT * FROM `02 churn-dataset - copy`;

RENAME TABLE `02 churn-dataset - copy` TO `customers`;

SELECT * FROM customers;

-- check is there any duplicate values in our data

with duplicate_handling as
(
select *,
row_number() over(partition by customerID,gender,SeniorCitizen,Partner,Dependents,Tenure,PhoneService,
								MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,
                                TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,
                                MonthlyCharges,TotalCharges,numAdminTickets,numTechTickets,Churn
					) as `rn`
from customers
)
select * 
from duplicate_handling
where `rn` not in(1);


/*Create A New Clomun Which Should Categorize Customers into categories Based on How long they are with us*/
set sql_safe_updates = 0;
update customers
 set  Tenure_category = case
     when Tenure >=1 and Tenure <=12 then "Low Tenure customers"
     when Tenure >=13 and Tenure <=36 then "Medium Tenure customers"
     when Tenure >=37 and Tenure <=72 then "High Tenure customers"
end;


/*create a categores for number of years customers with us*/
select distinct(Tenure_category) from customers;

select distinct(Tenure) 
from customers 
order by Tenure asc;

alter table customers add column
Loyality varchar(255);

set sql_safe_updates=0;
update customers
 set Loyality = case
      when Tenure <12 then "< 1 year"
      when Tenure >=12 and Tenure < 24 then "< 2 years"
      when Tenure >= 24 and Tenure < 36 then "< 3 years"
      when Tenure >= 36 and Tenure < 48 then "< 4 years"
      when Tenure >= 48 and Tenure < 60 then "< 5 years"
      when Tenure >= 60 and Tenure <= 72 then "< 6 years"
      else "unknown"
end;
 
 select distinct Loyality from customers order by Loyality ASC;

select * from customers;









