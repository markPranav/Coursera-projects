
#!/usr/bin/env python3

import os
import json
import locale
import sys
import reports
import emails


def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
  max_revenue = {"revenue": 0}
  max_sales = {'total_sales':0}
  year_sales={}
  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item
    # TODO: also handle max sales
    if item['total_sales'] > max_sales["total_sales"]:
      max_sales["total_sales"] = item["total_sales"]
      max_sales = item

    x=item["car"]["car_year"]
    #print(item["car"]["car_year"])
    #print(year_sales)
    '''if x in year_sales:
      year_sales[x] = year_sales[x] + item["total_sales"]
      #print(year_sales,item["car"]["car_year"])
    else:
      year_sales[x]=item["total_sales"]
      #print(year_sales,item["car"]["car_year"])'''
    try :
      year_sales[x] = year_sales[x] + item["total_sales"]
    except KeyError:
      year_sales[x]=item["total_sales"]

    # TODO: also handle most popular car_year
  print(year_sales.values())
  most_pop=max(year_sales.values())
  sales_in=list(year_sales.keys())[list(year_sales.values()).index(most_pop)]
  summary = [
    "The {} generated the most revenue: ${}".format(
      format_car(max_revenue["car"]), max_revenue["revenue"]),
    "The {} had most sales: {}".format(format_car(max_sales["car"]), max_sales["total_sales"]),
    "The most popular year was {} with {} sales".format(sales_in,most_pop)
  ]
  #print(year_sales["2007"])
  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data


def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("../car_sales.json")
  summary = process_data(data)
  print(summary)

  xsum=''
  xsum = '<br/>'.join(summary)
  # TODO: turn this into a PDF report
  table=cars_dict_to_table(data)
  reports.generate("/tmp/cars.pdf", "Sales summary for last month",xsum, table)
  # TODO: send the PDF report as an email attachment

  xsum = "\n".join(summary)
  sender = "automation@example.com"
  receiver = "{}@example.com".format(os.environ.get('USER'))
  subject = "Sales summary for last month"
  body = xsum
  message = emails.generate(sender, receiver, subject, body, "/tmp/cars.pdf")
  emails.send(message)

if __name__ == "__main__":
  main(sys.argv)