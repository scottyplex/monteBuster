# Monte Buster

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg) 
Tired of playing 5-card monte with your paychecks and bills? **Monte Buster** helps you map out your finances, so you know exactly which paycheck is best for each bill. Gain a clear view of your money's journey and confidently plan every payment.

---

## Table of Contents
- [About](#about)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## About

**Monte Buster** is a personal finance planning tool designed to help you navigate the common challenge of aligning floating paychecks (e.g., bi-weekly) with static monthly bill due dates. It helps prevent bounced payments and provides clarity on your cash flow by intelligently assigning bills to upcoming paychecks and showing your remaining balance.

This project was built to address a real-world financial problem and serves as a practical application of Python for financial management.

---

## Features

* **Pay Period Generation:** Automatically maps out all your paydays for the year based on your last paycheck date and frequency.
* **Bill Input:** Allows you to enter all your recurring and one-time bills with names, due dates, amounts, and categories.
* **Intelligent Bill Assignment:** Assigns each bill to the most appropriate upcoming paycheck to ensure timely payment.
* **Cash Flow Visualization:** Displays a detailed breakdown for each pay period, showing assigned bills and the remaining balance.
* **Spreadsheet Export:** Generates a comprehensive spreadsheet (e.g., CSV) for easy review and record-keeping.

---

## Getting Started

Follow these steps to get Monte Buster up and running on your local machine.

### Prerequisites

* **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
* **Git**: Install Git from [git-scm.com](https://git-scm.com/downloads).

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

*(You can add example prompts and a snippet of the output here once you have it running!)*

---

## Roadmap

This project is under active development. Here are some features planned for the future:

* **0% APR Promotion Calculator:** Calculate precise monthly payments for promotional credit card balances.
* **Google Calendar Integration:** Option to export paydays and bill reminders to a Google Calendar.
* **Graphical User Interface (GUI):** A more user-friendly visual interface.
* **Savings Goals Integration:** Ability to factor in and track specific savings goals.
* **Categorized Spending Reports:** More detailed breakdowns of spending by category.

---

## Contributing

This project is currently maintained by @scottyplex. While direct contributions (Pull Requests) are not actively being sought at this initial stage, feedback, bug reports, and feature suggestions are always welcome via the GitHub Issues page.

---

## License

This project is licensed under the [Business Source License (BSL)](LICENSE.md). Please see the `LICENSE.md` file for full details on usage rights, including commercial applications.
