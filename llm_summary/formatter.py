from bs4 import BeautifulSoup

def html_to_plain(html_string: str) -> str:
    soup = BeautifulSoup(html_string, "html.parser")
    return soup.get_text(separator="\n")

def build_prompt(year, region, data_dict) -> str:
    return f"""
In {year}, for the {region} Local Authority:

- The forecasted housing price is £{data_dict['housing_price']} 
  (95% confidence interval: £{data_dict['housing_price_ci_lower']} – £{data_dict['housing_price_ci_upper']}).

- The housing affordability index is {data_dict['affordability']}, 
  with a confidence range of {data_dict['affordability_ci_lower']} – {data_dict['affordability_ci_upper']}.

- The net additional dwellings expected are {data_dict['dwellings']}, 
  with a range of {data_dict['dwellings_ci_lower']} – {data_dict['dwellings_ci_upper']}.

Please generate a short summary in <p> and <b> HTML tags suitable for display in a webpage. 
Make it accessible to a general audience and under 120 words.
"""