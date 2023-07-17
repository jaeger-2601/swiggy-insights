# 📚🍔 Swiggy Insights 🍟📊

Swiggy Insights is a data analysis project that extracts valuable insights from orders made through Swiggy app. Through interactive data visualizations, it highlights trends, patterns, and user preferences.

Happy analyzing and bon appétit! 🍽️📊🔍

## 📋 Setup

This project utilizes jupytext for version control for Jupyter Notebooks. Use jupytext to convert the python file to notebook format.

1. Install dependencies
```
poetry install
```
2. Set up Jupytext to automatically sync your notebooks as scripts:
```
jupytext --set-formats ipynb,py swiggy.py  # Turn swiggy.ipynb into a paired ipynb/py notebook
jupytext --sync swiggy.py                  # Update whichever of swiggy.ipynb/swiggy.py is outdated
```

## 🌟 Contributing
Contributions to Swiggy Insights are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

When contributing, please ensure to follow the existing coding style and guidelines, and provide clear commit messages to maintain a clean and readable codebase.

## 📄 License
This project is licensed under the __<ins>GPL-3.0 license</ins>__.
