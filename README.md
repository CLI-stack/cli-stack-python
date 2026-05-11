# 100 Python Examples for Beginners

100 beginner-friendly Python scripts organized by category. Every script has a description explaining what it does, inline comments, and is self-contained.

## Categories

| # | Category | Scripts |
|---|----------|---------|
| 01 | [Scripting & Automation](01_scripting_automation/) | 01–20 |
| 02 | [Data Science](02_data_science/) | 21–40 |
| 03 | [Web](03_web/) | 41–60 |
| 04 | [CLI Tools](04_cli_tools/) | 61–80 |
| 05 | [Scientific Computing](05_scientific_computing/) | 81–100 |

## Quick Start

```bash
# Run any script directly
python 01_scripting_automation/01_hello_world.py

# Install common dependencies
pip install numpy pandas matplotlib scikit-learn flask fastapi requests beautifulsoup4
```

## Script Index

### 01 Scripting & Automation
| # | File | What it does |
|---|------|-------------|
| 01 | hello_world.py | Print text to the screen |
| 02 | variables_and_types.py | Integers, floats, strings, booleans |
| 03 | file_reader.py | Read a text file line by line |
| 04 | file_writer.py | Write and append to files |
| 05 | directory_lister.py | List files and folders |
| 06 | file_copier.py | Copy files with shutil |
| 07 | file_renamer.py | Rename files in bulk |
| 08 | csv_reader.py | Read CSV files |
| 09 | json_reader.py | Read and write JSON files |
| 10 | environment_variables.py | Access system env vars |
| 11 | command_runner.py | Run shell commands from Python |
| 12 | password_generator.py | Generate secure passwords |
| 13 | system_info.py | Get CPU, RAM, disk info |
| 14 | zip_extractor.py | Create and extract ZIP files |
| 15 | log_parser.py | Parse and filter log files |
| 16 | text_replacer.py | Find and replace in files |
| 17 | file_downloader.py | Download files from the internet |
| 18 | batch_file_renamer.py | Rename multiple files at once |
| 19 | scheduler.py | Schedule recurring tasks |
| 20 | regex_search.py | Search text with regular expressions |

### 02 Data Science
| # | File | What it does |
|---|------|-------------|
| 21 | basic_statistics.py | Mean, median, mode, std dev |
| 22 | list_operations.py | Python list methods |
| 23 | dictionary_operations.py | Python dict methods |
| 24 | numpy_basics.py | NumPy arrays |
| 25 | pandas_basics.py | Create and explore DataFrames |
| 26 | pandas_filter_sort.py | Filter and sort data |
| 27 | pandas_groupby.py | Aggregate data by groups |
| 28 | pandas_missing_values.py | Handle missing data |
| 29 | matplotlib_charts.py | Line, bar, pie charts |
| 30 | matplotlib_scatter.py | Scatter plots and histograms |
| 31 | data_normalization.py | Scale data for ML |
| 32 | simple_linear_regression.py | Predict with a straight line |
| 33 | classification.py | KNN classifier on iris data |
| 34 | kmeans_clustering.py | Group data automatically |
| 35 | pandas_merge.py | Join DataFrames like SQL |
| 36 | decision_tree.py | Tree-based classifier |
| 37 | train_test_split.py | Evaluate ML models fairly |
| 38 | word_count.py | Count word frequencies in text |
| 39 | correlation_analysis.py | Measure variable relationships |
| 40 | random_forest.py | Ensemble of decision trees |

### 03 Web
| # | File | What it does |
|---|------|-------------|
| 41 | flask_hello.py | Simplest Flask web app |
| 42 | flask_json_api.py | REST API with Flask |
| 43 | fastapi_hello.py | FastAPI with auto-docs |
| 44 | fastapi_crud.py | Full CRUD API with FastAPI |
| 45 | requests_get.py | HTTP GET requests |
| 46 | requests_post.py | HTTP POST/PUT/DELETE |
| 47 | web_scraper.py | Scrape a webpage |
| 48 | api_client.py | Reusable API client class |
| 49 | http_status_checker.py | Check if URLs are online |
| 50 | url_parser.py | Parse and build URLs |
| 51 | json_api_fetch.py | Fetch real API data |
| 52 | session_handling.py | Sessions, cookies, auth |
| 53 | flask_form.py | Handle HTML form submissions |
| 54 | rate_limiter.py | Limit API request rate |
| 55 | beautifulsoup_parse.py | Parse HTML structure |
| 56 | webhook_handler.py | Receive webhook events |
| 57 | flask_template.py | Flask with Jinja2 templates |
| 58 | github_api.py | GitHub REST API client |
| 59 | rss_reader.py | Read RSS feeds |
| 60 | file_upload_api.py | Upload files via HTTP |

### 04 CLI Tools
| # | File | What it does |
|---|------|-------------|
| 61 | simple_cli.py | Interactive CLI with input() |
| 62 | argparse_basic.py | CLI with arguments |
| 63 | argparse_subcommands.py | CLI with subcommands (like git) |
| 64 | progress_bar.py | Progress bar in terminal |
| 65 | color_output.py | Colored terminal text |
| 66 | interactive_menu.py | Menu-driven CLI app |
| 67 | calculator_cli.py | Math expression evaluator |
| 68 | word_counter.py | Count words in files |
| 69 | unit_converter.py | Convert length, weight, temp |
| 70 | todo_cli.py | Todo list with file storage |
| 71 | timer_cli.py | Countdown timer |
| 72 | grep_clone.py | Search text in files |
| 73 | find_files.py | Find files by name/size |
| 74 | csv_to_json.py | Convert CSV to JSON |
| 75 | json_formatter.py | Pretty-print and validate JSON |
| 76 | base64_tool.py | Encode/decode Base64 |
| 77 | hash_generator.py | MD5/SHA256 file hashes |
| 78 | ping_tool.py | Check host connectivity |
| 79 | file_size_checker.py | Find largest files |
| 80 | datetime_cli.py | Date formatting and arithmetic |

### 05 Scientific Computing
| # | File | What it does |
|---|------|-------------|
| 81 | basic_math.py | Python math module |
| 82 | matrix_operations.py | Matrix math with NumPy |
| 83 | solving_equations.py | Solve linear equation systems |
| 84 | statistics_scipy.py | T-tests and hypothesis testing |
| 85 | monte_carlo.py | Estimate π by random sampling |
| 86 | numerical_integration.py | Area under a curve |
| 87 | sorting_algorithms.py | Bubble, merge, quick sort |
| 88 | search_algorithms.py | Linear vs binary search |
| 89 | recursion_examples.py | Factorial, Fibonacci, flatten |
| 90 | data_structures.py | Stack, Queue, Linked List |
| 91 | probability_distributions.py | Normal, Poisson, binomial |
| 92 | curve_fitting.py | Fit a function to data |
| 93 | interpolation.py | Estimate values between points |
| 94 | optimization.py | Find minimum of a function |
| 95 | fourier_transform.py | Frequency analysis of signals |
| 96 | fibonacci_advanced.py | 5 ways to compute Fibonacci |
| 97 | prime_numbers.py | Sieve of Eratosthenes |
| 98 | string_operations.py | Comprehensive string guide |
| 99 | image_processing.py | PIL/Pillow image editing |
| 100 | graph_theory.py | Networks with NetworkX |
