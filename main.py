import zipfile
import gzip
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
import os

def read_gz_from_zip(zip_path):
    data = []
    subscriber = []
    subscribers = []
    date = ""
    started = 0

    # Open the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Iterate over the files in the ZIP
        for file_info in zip_ref.infolist():
            # Check if the file is a .gz file
            if file_info.filename.endswith('.gz'):
                # Open the .gz file within the ZIP
                with zip_ref.open(file_info) as gz_file:
                    with gzip.open(gz_file, 'rt', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # Initialize a transaction dictionary
                        transaction = {}
                        for line in lines:
                            if "START" in line:
                                date = line.split()[0].strip()
                            if "transaction:" in line.lower():
                                started = 1
                            elif started == 1:
                                subscriber.append(line.strip(" ,\n").split(":", 1)[1].strip(" '"))
                                if "newBalance" in line:
                                    if len(subscriber) == 13:
                                        subscriber.append(date)
                                        subscribers.append(subscriber)
                                    subscriber = []
                                    started = 0

    df = pd.DataFrame(subscribers, columns=["id", "type", "source", "action", "userId", "paymentBalance",
                                             "updatePaymentBalance", "metadata", "currency", "amount", "vat",
                                             "oldBalance", "newBalance", "date"])
    return df

def convert_columns(df):
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['newBalance'] = pd.to_numeric(df['newBalance'], errors='coerce')
    df['oldBalance'] = pd.to_numeric(df['oldBalance'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.95)
    IQR = Q3 - Q1
#     lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR
    df_outliers =  df[(df[column] > upper_limit)]
    df = df[(df[column] <= upper_limit)]
    return df, df_outliers, upper_limit

def plot_outliers(df_outliers, column, output_dir):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_outliers, x='date', y=column, hue='type')
    plt.title(f'Outliers in {column}')
    plt.xlabel('Date')
    plt.ylabel(column)
    plt.legend()
    plt.savefig(os.path.join(output_dir, f'outliers_in_{column}.png'))
    plt.close()

def general_eda(df, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Distribution of transaction amounts
    plt.figure(figsize=(10, 6))
    sns.histplot(df['amount'], bins=50, kde=True)
    plt.title('Distribution of Transaction Amounts')
    plt.xlabel('Amount')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, 'distribution_of_transaction_amounts.png'))
    plt.close()

    # Transaction types
    plt.figure(figsize=(10, 6))
    sns.countplot(x='type', data=df)
    plt.title('Distribution of Transaction Types')
    plt.xlabel('Transaction Type')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, 'distribution_of_transaction_types.png'))
    plt.close()

    # Trends over time
    df.set_index('date', inplace=True)
    df.resample('M').size().plot(figsize=(10, 6))
    plt.title('Transactions Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Transactions')
    plt.savefig(os.path.join(output_dir, 'transactions_over_time.png'))
    plt.close()

    # Balance distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['newBalance'], bins=50, kde=True)
    plt.title('Distribution of New Balances')
    plt.xlabel('New Balance')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, 'distribution_of_new_balances.png'))
    plt.close()

    # Payment balance distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['paymentBalance'], bins=50, kde=True)
    plt.title('Distribution of Payment Balances')
    plt.xlabel('Payment Balance')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, 'distribution_of_payment_balances.png'))
    plt.close()
    
    # Plot the most common actions
    plt.figure(figsize=(10, 14))
    top_actions = df['action'].value_counts().head(10)
    top_actions.plot(kind='bar')
    plt.title('Top Actions')
    plt.xlabel('Action')
    plt.ylabel('Number of Transactions')
    plt.savefig(os.path.join(output_dir, 'Frequency of Action.png'))
    plt.close()
    
    # Plot the number of transactions by currency
    plt.figure(figsize=(10, 10))
    currency_counts = df['currency'].value_counts()
    currency_counts.plot(kind='bar')
    plt.title('Transactions by Currency')
    plt.xlabel('Currency')
    plt.ylabel('Number of Transactions')
    plt.savefig(os.path.join(output_dir, 'Frequency of Currency.png'))
    plt.close()


def subscriber_eda(df, user_id, output_dir):
    subscriber_data = df[df['userId'] == user_id]

    if subscriber_data.empty:
        print(f"No data found for subscriber {user_id}")
        return

    # Transaction history
    plt.figure(figsize=(10, 6))
    subscriber_data['amount'].plot()
    plt.title(f'Transaction Amounts Over Time for Subscriber {user_id}')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.savefig(os.path.join(output_dir, f'transaction_amounts_{user_id}.png'))
    plt.close()

    # Balance changes over time
    plt.figure(figsize=(10, 6))
    subscriber_data[['oldBalance', 'newBalance']].plot()
    plt.title(f'Balance Changes Over Time for Subscriber {user_id}')
    plt.xlabel('Date')
    plt.ylabel('Balance')
    plt.savefig(os.path.join(output_dir, f'balance_changes_{user_id}.png'))
    plt.close()

    # Transaction types
    plt.figure(figsize=(10, 6))
    sns.countplot(x='type', data=subscriber_data)
    plt.title(f'Transaction Types for Subscriber {user_id}')
    plt.xlabel('Transaction Type')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'transaction_types_{user_id}.png'))
    plt.close()

    # Distribution of amounts for the subscriber
    plt.figure(figsize=(10, 6))
    sns.histplot(subscriber_data['amount'], bins=50, kde=True)
    plt.title(f'Distribution of Transaction Amounts for Subscriber {user_id}')
    plt.xlabel('Amount')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'distribution_of_transaction_amounts_{user_id}.png'))
    plt.close()

    # Distribution of new balances for the subscriber
    plt.figure(figsize=(10, 6))
    sns.histplot(subscriber_data['newBalance'], bins=50, kde=True)
    plt.title(f'Distribution of New Balances for Subscriber {user_id}')
    plt.xlabel('New Balance')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'distribution_of_new_balances_{user_id}.png'))
    plt.close()

    # Distribution of payment balances for the subscriber
    plt.figure(figsize=(10, 6))
    sns.histplot(subscriber_data['paymentBalance'], bins=50, kde=True)
    plt.title(f'Distribution of Payment Balances for Subscriber {user_id}')
    plt.xlabel('Payment Balance')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'distribution_of_payment_balances_{user_id}.png'))
    plt.close()
    
    # Plot the most common actions
    
    plt.figure(figsize=(10, 14))
    top_actions = df['action'].value_counts().head(10)
    top_actions.plot(kind='bar')
    plt.title(f'Top Actions for Subscriber {user_id}')
    plt.xlabel('Action')
    plt.ylabel('Number of Transactions')
    plt.savefig(os.path.join(output_dir, f'distribution_of_action_{user_id}.png'))
    plt.close()
    
    plt.figure(figsize=(10, 10))
    currency_counts = df['currency'].value_counts()
    currency_counts.plot(kind='bar')
    plt.title(f'Transactions by Currency {user_id}')
    plt.xlabel('Currency')
    plt.ylabel('Number of Transactions')
    plt.savefig(os.path.join(output_dir, f'Frequency of Currency {user_id}.png'))
    plt.close()


def identify_overdraft_users(df, output_dir):
    # Check if balance becomes negative after each transaction
    overdraft_users = df[df['newBalance'] < 0]['userId'].unique()

    # Export overdraft users list to a file
    with open(os.path.join(output_dir, 'overdraft_users.txt'), 'w') as f:
        for user_id in overdraft_users:
            f.write(user_id + '\n')

    return overdraft_users

def export_reports_to_excel(df, output_path):
    # Convert datetime column to timezone naive
    df['date'] = df['date'].dt.tz_localize(None)

    # Export DataFrame to Excel
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name='Transactions', index=False)

def main(output_dir):
    # Determine the path to the ZIP file based on the operating system
    if os.name == 'posix':  # Check if the operating system is Unix-like (Linux, macOS)
        zip_path = os.path.join(os.getcwd(), 'balance-sync-logs.zip')
    elif os.name == 'nt':  # Check if the operating system is Windows
        zip_path = os.path.join(os.getcwd(), 'balance-sync-logs.zip')
    else:
        raise OSError("Unsupported operating system")

    # Read data from zip and apply EDA
    df = read_gz_from_zip(zip_path)

    # Convert columns to appropriate data types
    df = convert_columns(df)

    # Remove outliers
    df, df_outliers, _ = remove_outliers(df, 'amount')

    # Perform general EDA
    general_eda(df, output_dir)

    # Plot outliers
    plot_outliers(df_outliers, 'amount', output_dir)

    # Identify overdraft users
    overdraft_users = identify_overdraft_users(df, output_dir)

    # Perform EDA for each overdraft user
    for user_id in overdraft_users:
        subscriber_output_dir = os.path.join(output_dir, f'subscriber_{user_id}')
        os.makedirs(subscriber_output_dir, exist_ok=True)
        subscriber_eda(df[df['userId'] == user_id], user_id, subscriber_output_dir)

    # Export reports to Excel
    df.reset_index(inplace=True)
    export_reports_to_excel(df, os.path.join(output_dir, 'transactions.xlsx'))
if __name__ == "__main__":
    # Output directory
    output_dir = r'output_directory'
    os.makedirs(output_dir, exist_ok=True)
    # Call main function
    main(output_dir)
