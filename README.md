# RFM Customer Segmentation with Online Retail Data

This repository contains a project on customer segmentation using RFM (Recency, Frequency, Monetary) analysis. The project leverages an online retail dataset from an e-commerce company to categorize customers into different segments, which can be used for targeted marketing strategies.

## Table of Contents

- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The goal of this project is to perform customer segmentation using RFM analysis. By analyzing customer behavior based on their purchase history, we can divide customers into different segments and devise targeted marketing strategies to improve customer retention and sales.

## Dataset

The dataset used in this project is the "Online Retail II" dataset from the UCI Machine Learning Repository. It contains transactions from an online retailer based in the UK between 01/12/2009 and 09/12/2011.

### Features

- `InvoiceNo`: Unique invoice number. Canceled transactions start with 'C'.
- `StockCode`: Unique product code.
- `Description`: Product name.
- `Quantity`: The number of units of the product.
- `InvoiceDate`: The date and time when the transaction was generated.
- `UnitPrice`: Unit price of the product in GBP.
- `CustomerID`: Unique customer identifier.
- `Country`: The country where the customer resides.

## Installation

To run this project, you need to have Python installed on your system along with the necessary libraries. Follow the steps below to set up the environment:

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    ```
2. Change the directory:
    ```sh
    cd your-repo-name
    ```
3. Create a virtual environment and activate it:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Follow these steps to run the project:

1. Ensure the dataset file `online_retail_II.xlsx` is placed in the `datasets` directory.
2. Run the RFM segmentation script:
    ```sh
    python rfm_segmentation.py
    ```
3. The results will be saved in the `rfm` directory as `rfm.csv` and `new_customers.csv`.

## Project Structure

- ├── .idea 
- ├── cltv 
- ├── cltv_prediction 
- ├── datasets 
- │ └── online_retail_II.xlsx 
- ├── rfm
- │ └── rfm.csv 
- ├── .DS_Store 
- ├── README.md 
- ├── rfm_segmentation.py 
- └── requirements.txt


## Results

The project outputs two CSV files:
- `rfm.csv`: Contains the RFM scores and segments for all customers.
- `new_customers.csv`: Contains the IDs of new customers identified through the RFM analysis.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
