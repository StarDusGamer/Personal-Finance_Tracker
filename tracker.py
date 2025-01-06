import sys
import csv
import pandas
import argparse
import numpy
import os
import re
import matplotlib.pyplot as matplot

'''
Completed:
    Table of net gain split into years by month
Ideas:
    Spending Over Time Line Graph
    Table of Expenses by Category
    Goals for Saving, and How You Have Met Those Goals
        Make a new goal csv file on first run that has the columns
        Desired year, Desired month, saving or spending goal, 
        short description, amount
        Then parse the set goal and display the information needed
'''


def parseArguments():
    parser = argparse.ArgumentParser(description="Finance Tracker")
    parser.add_argument(
        "input_file",
        help=
            "The csv file to store your finances")
    args = parser.parse_args()
    global inputfile
    inputfile = args.input_file

def add_transaction():
    date = input("Please input the following information:\nDate (YY-MM-DD) of Transaction:\n")
    category = input("Under what Category does it fall under:\n")
    description = input("Give a short (1-5 Words) description:\n")
    amount = input("How much was the transaction (Use + for income, - for expense):\n")
    _type = input("Was is an expense of income:\n")
    with open(inputfile, mode = 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, description, amount, _type])
    print(f"Added:\n{date} : {category} : {_type} : {amount}\n{description}\n")

def view_transaction(given_file):
    return pandas.read_csv(given_file)

def summarize_spending():
    spending = view_transaction(inputfile)
    totalIncome = spending[spending['type'] == 'income']['amount'].sum()
    totalExpenses = spending[spending['type'] == 'expense']['amount'].sum()
    balance = totalIncome + totalExpenses
    expenseByCat = spending[spending['type'] == 'expense'].groupby('category')['amount'].sum()
    return [totalIncome,totalExpenses,balance,expenseByCat]

def show_finances_by_month():
    spending = view_transaction(inputfile)
    summary = summarize_spending()

    years = spending['date'].str[:2]
    spending = spending.groupby(years)
   
    table = matplot.figure(figsize=(12,12))
    for year, elem in spending:
        createTable(year,elem, table)
        print(f"\nYear: 20{year}")
        print(elem)
    matplot.tight_layout(pad=1, w_pad=0, h_pad=0)
    matplot.show()

def createTable(year,transactions,table):
    columns = ['Income', 'Expense', 'Net Gain']
    rows = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    transactions['month'] = transactions['date'].str[3:5]

    months = transactions.groupby('month')
    cell_text = months['amount'].agg(
            int1 = lambda x: x[x > 0].sum(),
            int2 = lambda x: x[x < 0].sum(),
            int3 = 'sum')
    cell_text = cell_text.reindex([f'{i:02d}' for i in range(1,13)], fill_value = 0)
    cell_text = cell_text.values.tolist()
    print(cell_text)
    colors = ["#f5f5f5"] * len(rows)
    subTb = table.add_subplot(4, len(columns), len(table.axes) + 1)
    subTb.set_title(f'20{year}', y=1.038)
    subTable = subTb.table(cellText=cell_text,
                rowLabels=rows,
                rowColours=colors,
                colLabels=columns,
                loc='center')

    subTb.axis('off')

def check_condition(inputMSG, options, errorMSG):
    while True:
        user = input(inputMSG)
        if bool(re.match(options, user)):
            break
        else:
            print(errorMSG)
    return user

def add_goal():
    print(os.path.exists('goals.csv'))
    if not os.path.exists('goals.csv'):
        print("Making New File\n")
        with open('goals.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['start', 'date', 'type', 'amount', 'description'])
    print("Please Input the following Information:\n")

    start = check_condition("What is the Begining Date (YY-MM-DD) for the Goal:\n",
                           r"^\d{2}-\d{2}-\d{2}$",
                           "Please Follow the Format (YY-MM-DD)\n")

    date = check_condition("What is the Desired Complete-By Date (YY-MM-DD) for the Goal:\n",
                           r"^\d{2}-\d{2}-\d{2}$",
                           "Please Follow the Format (YY-MM-DD)\n")

    goalType = check_condition("Is it a saving or spending Goal:\n",
                               r"^(saving|spending)$",
                               "Please Enter Either \"saving\" or \"spending\"\n")

    amount = check_condition("What is the amount for the goal:\n",
                             r"^\d+$",
                             "Please Input a integer value >= 0\n")

    description = check_condition("Give a short description for the goal:\n",
                                  r"^.{1,}$",
                                  "Please Enter at least 1 Word\n")

    with open('goals.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, goalType, amount, description])

def show_goal_progress():
    goals = view_transaction('goals.csv')
    progress = view_transaction(inputfile)
    pie = matplot.figure(figsize=(12,12))
    
    for index, row in goals.iterrows():
        print(f"Line {index + 1}")
        print(row)
        #Put Date Splitting Here

def create_pie_chart(goal, progress):
    return

def main():
    args = parseArguments()
    while True:
        user = input("""What Would You Like to do:\n
                     a) add transaction\n
                     b) set goal\n
                     c) show net gain by month\n
                     d) show goal progress\n
                     x) terminate\n""")
        options = {'a' : add_transaction,
                   'b' : add_goal,
                   'c' : show_finances_by_month,
                   'd' : show_goal_progress,
                   'x' : sys.exit
                }
        chosenOption = options.get(user, lambda: print("Invalid choice. Please select a valid option.\n\n"))
        chosenOption()
    return 0

main()
