import numpy as np
import matplotlib.pyplot as plt
import math

'''set initial parameters - change depending on plan'''

#information about company and site names to be used on the graph
companyName='Aura Wind Energy Solutions'
siteName='Corlic Hill Community Wind Farm'

#turbine type information to be used in calculations
t1Count = 0.0 
t2Count = 7.0 
t3Count = 0.0 

#distance from grid in KM
gridConnection = 2.5 

#percentage of time turbines can produce electricity, expressed as a decimal from 0 to 1
capFactor = 0.458 

#time in years for baseline surveys
surveyTime=1

#time taken to construct windfarm, expressed as a decimal from 0 to 1 year
constructionTime=0.75

#if applicable, how much MWh anually needs to be compensated to another farm due to wake losses
otherFarmLoss=1340
'''uncomment below if user input during runtime is desired'''
'''
companyName=input("What is the name of your company?")
siteName=input("What is the name of the wind farm site?")
t1Count=float(input("How many turbines of type 1?\n"))
t2Count=float(input("How many turbines of type 2?\n"))
t3Count=float(input("How many turbines of type 3?\n"))
gridConnection=float(input("How far away are you from the grid in km?"))
capFactor=float(input("What is your capacity factor, from 0 to 1?"))
surveyTime=inputfloat(("How long is the baseline survey expected to take in years?"))
constructionTime=float(input("how long is the construction time expected to take in years, from 0 to 1"))
'''

'''Constants based on the brief - shouldn't need to change'''
timeHorizon=25#how long project runs for in years
electricityPrice=70/1000000 #electricity price in £/MWh
gridCost=0.75 #one off payment of £750,000 per kilometer
balanceOfPlant=1.25 #one off payment of 25% of turbine cost
# cost of each turbine in millions of pounds
t1Cost=1.29 
t2Cost=2.322 
t3Cost=4.3344 
#turbine rating in MWh
t1Power=2.5 
t2Power=3.6 
t3Power=5.6
maintenance=0.1 #annual maintenance costs
fixedRent=6000/1000000 #get fixed rent in millions
fixedRentLater=8000/1000000 #fixed rent after 13 years in millions
landRent=0.06 #6 percent before 13 years and 6 percent after for rent
landRentLater=0.08


#get total turbine cost based on sum of turbines and their costs
turbineCost = t1Count*t1Cost+t2Count*t2Cost+t3Count*t3Cost
#get total initial cost by adding balance of plant costs and grid connection
totalInitCost=turbineCost*balanceOfPlant+(gridConnection*gridCost)

#may need to add EIA/survey cost, reasonable number?

#may need social impact costs
#may need environmental impact costs

#calculate total power rating based on sum of turbines and their power ratings
powerRating=t1Count*t1Power+t2Count*t2Power+t3Count*t3Power
powerGeneratedHourly=powerRating*capFactor
powerGenAnnually=powerGeneratedHourly*24*365
#get annual revenue from power generation figure, to be used in the loop later
annualInitialRevenue=powerGenAnnually*electricityPrice

#calculate revenue to be compensated to another farm in case of wake loss
compensation=otherFarmLoss*electricityPrice
compensationRatio=1-(otherFarmLoss/powerGenAnnually)

#calculate and set amounts to be used in the time series loop
maintenanceCost=turbineCost*maintenance
initLoanAmount=totalInitCost
loanAmount=initLoanAmount
thisMaintenance=0

#calculate loan size required
initLoanSize=(totalInitCost*(1+interestRate))+(fixedRent*(constructionTime+surveyTime))+maintenanceCost+landRent*(annualInitialRevenue*(1-constructionTime))-(annualInitialRevenue*(1-constructionTime))

#section to calculate the loan interest rate, based on loan size
if initLoanSize<50:
    interestRate=0.01
elif initLoanSize<90:
    interestRate=0.03
elif initLoanSize<110:
    interestRate=0.05
else:
    interestRate=0.08

#create empty arrays which will be popuated in the time series 
revenueArray=[]
costArray=[]
profitArray=[]
repaymentArray=[]
maintenanceArray=[]
rentArray=[]
compensationArray=[]

#set initial balance to be used in the time series, to calculate loan repayment schedule
balance = initLoanSize-totalInitCost

#loop for the amount of years set earlier
for x in range(0,timeHorizon):
    '''calculate revenue generated based on current project year
    and work out how much money needs to be sent away to another farm if applicable'''
    
    #no revenue is generated due to the baseline survey being conducted
    if x<math.ceil(surveyTime): 
        annualRevenue=0 
        annualCompensation=0
    #reduce revenue by duration of construction time 
    elif x<math.ceil(surveyTime+constructionTime):
        annualRevenue = annualInitialRevenue * (1-constructionTime) 
        annualCompensation=compensation*(1-constructionTime) 
    #otherwise, we assume full initial revenue as estimated earlier
    else:
        annualRevenue = annualInitialRevenue
        annualCompensation=compensation
    #increase balance by the revenue generated this year, and add it to the revenue array
    balance+=annualRevenue
    revenueArray.append(annualRevenue)    
    #do the same for compensation
    balance-=annualCompensation
    compensationArray.append(annualCompensation)
    
    #for the first 13 years rent is lower
    if (x<=13): 
        annualRent=fixedRent+landRent*annualRevenue
    else:
        annualRent=fixedRentLater+landRentLater*annualRevenue
        
    #decrease balance by the rent paid this year, and add it to the rent array
    balance-=annualRent
    rentArray.append(annualRent)
    
    '''calculate maintenance costs based on how long surveying takes'''
    #only included once construction starts
    if(x>math.ceil(surveyTime)):
        thisMaintenance=maintenanceCost        
    #decrease balance by the rent paid this year, and add it to the rent array
    maintenanceArray.append(thisMaintenance)
    balance-=thisMaintenance

    
    #may need to add social and environmental costs
    
    '''calculate loan repayment amounts'''
    #only applies if there is still a loan left
    if (loanAmount>0):
        interestIncrease=loanAmount*interestRate
        loanAmount*=(1+interestRate) #add interest to loan before repayment 
        #don't repay loan while no revenue is generated
        if(annualRevenue==0):
            repaymentAmount=0
        #repay loan depending on how much is left
        elif (loanAmount>balance):
            repaymentAmount=balance
            loanAmount-=repaymentAmount
        else:
            repaymentAmount=loanAmount
            loanAmount=0
    else:
        repaymentAmount=0
    repaymentArray.append(repaymentAmount)
    balance-=repaymentAmount
    
    #add data to arrays
    costArray.append(thisMaintenance+repaymentAmount+annualRent+annualCompensation)
    annualProfit=revenueArray[x]-costArray[x]
    profitArray.append(annualProfit)


#calculate totals
totalProfit = np.sum(profitArray)
totalRevenue= np.sum(revenueArray)
totalCost=np.sum(costArray)
totalRentPaid=np.sum(rentArray)
totalMaintenancePaid=np.sum(maintenanceArray)
totalLoanPaid=np.sum(repaymentArray)
totalCompensationPaid=np.sum(compensationArray)

'''Print estimated costs and revenue'''
print(companyName + " - " + siteName)
print('Cumulative:')
print(f'Rent Costs: £{round(totalRentPaid,1)} million')
print(f'Loan Principle Repaid: £{round((initLoanSize),1)} million')
print(f'Interest Paid: £{round((totalLoanPaid-initLoanSize),1)} million')
print(f'Compensation Paid: £{round(totalCompensationPaid,1)} million')
print(f'Maintenance costs: £{round(totalMaintenancePaid,1)} million')
print(f'Costs: £{round(totalCost,1)} million')
print(f'Revenue: £{round(totalRevenue,1)} million')
print(f'Profit: £{round(totalProfit,1)} million\n')


#calculate and print financial metrics
ROI=(totalProfit/initLoanAmount)*100 #return on investment
CAGR=((totalProfit/initLoanAmount)**(1/25)-1)*100
print(f'Return on investment (ROI): {round(ROI)}%')
print(f'Compound Annual Growth Rate (CAGR): {round(CAGR,2)}%')

#additional information about project
print(f'Loan repaid by year {(np.array(repaymentArray)[1:].tolist().index(0))+1}')

#create cumulative arrays based on annual data
cumProfitArray=np.cumsum(profitArray)
cumRentArray=np.cumsum(rentArray)
cumMaintenanceArray=np.cumsum(maintenanceArray)
cumRepaymentArray=np.cumsum(repaymentArray)
cumRevenueArray=np.cumsum(revenueArray)
cumCompensationArray=np.cumsum(compensationArray)

#plot some graphs to display information
ind=np.arange(start=1,stop=26,step=1)
plt.figure(figsize=(10, 8))
colours = ['red' if (x < 0) else 'green' for x in profitArray ]
plt.bar(ind, profitArray, width=0.8, label='Revenue', color=colours)
plt.title(siteName + " Projected Annual Profit/Loss")
plt.ylabel("Millions of Pounds")
plt.xlabel("Year of Project")
plt.show()
'''
plt.figure(figsize=(10, 8))
plt.plot(ind,cumProfitArray,linewidth=5)
plt.ylabel("Millions of Pounds")
plt.xlabel("Year of Project")
plt.title(siteName + " Projected Cumulative Profit/Loss")
plt.show()
'''
added=np.add(np.negative(rentArray),np.negative(maintenanceArray))
plt.figure(figsize=(10, 8))
plt.plot(ind,profitArray,linewidth=8.0,color='black')
plt.plot(ind,profitArray,linewidth=5.0,label='Profit')
plt.bar(ind, revenueArray, width=0.8, label='Revenue', color='green')
plt.bar(ind, np.negative(repaymentArray), width=0.8, label='Loan', color='brown', bottom=added)
plt.bar(ind, np.negative(rentArray), width=0.8, label='Rent', color='red', bottom=np.negative(maintenanceArray))
plt.bar(ind, np.negative(maintenanceArray), width=0.8, label='Maintenance', color='orange')
plt.bar(ind, np.negative(compensationArray), width=0.8, label='Compensation', color='purple', bottom=np.add(np.negative(repaymentArray), added))

plt.xticks(ind,ind)
plt.ylabel("Millions of Pounds")
plt.xlabel("Year of Project")
plt.legend(loc="upper left")
plt.title(siteName + " Projected Revenue and Costs")
plt.show()

plt.figure(figsize=(10, 8))
plt.plot(ind,cumProfitArray,linewidth=8.0,color='black')
plt.plot(ind,cumProfitArray,linewidth=5.0,label='Profit')
plt.stackplot(ind,cumRevenueArray,labels=['Revenue'],colors=['green'])
plt.stackplot(ind,np.negative(cumRepaymentArray), np.negative(cumRentArray), np.negative(cumMaintenanceArray),np.negative(cumCompensationArray), labels=['Loan','Rent','Maintenance', 'Compensation'],colors=['brown','red','orange','purple'])
plt.legend(loc='upper left')
plt.xlabel("Year of Project")
plt.ylabel("Millions of Pounds")
plt.title(siteName + " Projected Cumulative Revenue and Costs")
plt.show()