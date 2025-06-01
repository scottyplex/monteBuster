# Monte Buster

Tired of playing 5-card monte with your paychecks and bills? **Monte Buster** helps you map out your finances, so you know exactly which paycheck is best for each bill. Gain a clear view of your money's journey and confidently plan every payment.

## Table of Contents

- [Monte Buster](#monte-buster)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Roadmap](#roadmap)
  - [Contributing](#contributing)
  - [License](#license)

## About

**Monte Buster** is a personal finance planning tool designed to help you navigate the common challenge of aligning floating paychecks (e.g., bi-weekly) with static monthly bill due dates. It helps prevent bounced payments and provides clarity on your cash flow by intelligently assigning bills to upcoming paychecks and showing your remaining balance.

This project was built to address a real-world financial problem and serves as a practical application of Python for financial management.

## Features

* **Pay Period Generation:** Automatically maps out all your paydays for the year based on your last paycheck date and frequency.

* **Bill Input:** Allows you to enter all your recurring and one-time bills with names, due dates, amounts, and categories.

* **Intelligent Bill Assignment:** Assigns each bill to the most appropriate upcoming paycheck to ensure timely payment.

* **Cash Flow Visualization:** Displays a detailed breakdown for each pay period, showing assigned bills and the remaining balance.

* **Debt Optimization Simulation:**

  * Simulate the impact of making **extra payments** on your debts to see total interest saved and time to payoff.

  * Model **principal-only payments** to understand their direct effect on reducing your loan balance and overall cost.

  * Provides a clear comparison between minimum payments and optimized payment strategies.

* **Comprehensive Spreadsheet Export:** Generates a detailed Excel spreadsheet (`.xlsx`) including:

  * High-level paycheck summaries.

  * Detailed paycheck breakdowns for granular analysis.

  * Debt progress reports showing balance, interest, and principal paid over time.

  * Credit utilization analysis to help manage credit scores.

  * **Visual Charts:** Includes a stacked column chart in the spreadsheet to visually represent paycheck expense breakdowns.

## Getting Started

Follow these steps to get Monte Buster up and running on your local machine.

### Prerequisites

* **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).

* **Git**: Install Git from [git-scm.com](https://git-scm.com/downloads).

* **pandas**: For data manipulation and spreadsheet generation.

* **XlsxWriter**: For writing Excel `.xlsx` files.

### Installation

1.  **Clone the repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/scottyplex/monteBuster.git
    ```

2.  **Navigate into the project directory:**
    ```bash
    cd monteBuster
    ```

3.  **Install dependencies (Optional, for now):**
    *(You'll create a `requirements.txt` file later if you install libraries like `icalendar` or `openpyxl`. For now, you might not have any beyond Python's standard library.)*
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

Once installed, you can run the application from your terminal:
```bash
python src/main.py
```

The program will then guide you through a series of prompts to input your pay information and bills. After processing, it will display a summary of your paychecks and generate a detailed spreadsheet in the project directory.

*(add example prompts and a snippet of the output here once you have it running!)*

---

The program will then guide you through a series of prompts to input your pay information and bills. You can choose to add new bills, view/edit existing ones, run a full financial plan simulation, or optimize specific debt payments. After a simulation, a comprehensive Excel spreadsheet (`financial_plan.xlsx`) will be generated in the `data/` directory, providing detailed reports and charts.

## Roadmap

This project is under active development. Here are some features planned for the future:

* **Google Calendar Integration:** Option to export paydays and bill reminders to a Google Calendar.

* **Graphical User Interface (GUI):** A more user-friendly visual interface.

* **Savings Goals Integration:** Ability to factor in and track specific savings goals.

* **Categorized Spending Reports:** More detailed breakdowns of spending by category, potentially with more advanced visualizations.

* **Historical Data Tracking:** Allow users to input past payment data for more robust analysis.

* **Cloud Synchronization:** Option to store and sync financial data securely in the cloud.

## Contributing

This project is currently maintained by @scottyplex. While direct contributions (Pull Requests) are not actively being sought at this initial stage, feedback, bug reports, and feature suggestions are always welcome via the GitHub Issues page.

## License

This project is licensed under the [Business Source License (BSL)](LICENSE.md). Please see the `LICENSE.md` file for full details on usage rights, including commercial applications.