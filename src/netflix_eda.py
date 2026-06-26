import os
import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for premium visualizations
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11

# Netflix Palette: Charcoal and Crimson Red
NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221F1F"
NETFLIX_LIGHT = "#F5F5F1"
CUSTOM_PALETTE = [NETFLIX_RED, "#564d4d", "#831010", "#464646", "#141414"]

def setup_directories():
    """Create data and plots directories if they don't exist."""
    print("Setting up directory structure...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

def download_dataset():
    """Download Netflix titles dataset from a reliable public raw URL."""
    url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-04-20/netflix_titles.csv"
    dest = os.path.join("data", "netflix_titles.csv")
    
    if not os.path.exists(dest):
        print(f"Downloading dataset from {url}...")
        try:
            urllib.request.urlretrieve(url, dest)
            print("Download completed successfully!")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            raise e
    else:
        print("Dataset already exists locally.")
    return dest

def load_and_explore(file_path):
    """Load the dataset and perform basic shape and data type inspections."""
    print("\n--- Phase 1: Data Exploration ---")
    df = pd.read_csv(file_path)
    
    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns and Data Types:")
    print(df.dtypes)
    
    print("\nMissing values per column:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            percentage = (count / len(df)) * 100
            print(f"  {col}: {count} ({percentage:.2f}%) missing")
            
    return df

def clean_data(df):
    """Clean the data, handle missing values, and extract features."""
    print("\n--- Phase 2: Data Cleaning & Feature Engineering ---")
    df_cleaned = df.copy()
    
    # 1. Fill missing values
    df_cleaned['director'] = df_cleaned['director'].fillna('Unknown Director')
    df_cleaned['cast'] = df_cleaned['cast'].fillna('No Cast')
    df_cleaned['country'] = df_cleaned['country'].fillna('Unknown')
    
    # Mode imputation for rating
    mode_rating = df_cleaned['rating'].mode()[0]
    df_cleaned['rating'] = df_cleaned['rating'].fillna(mode_rating)
    
    # Drop rows with null date_added as they are very few (~10 rows)
    df_cleaned = df_cleaned.dropna(subset=['date_added'])
    
    # 2. Fix data types & extract date features
    df_cleaned['date_added'] = df_cleaned['date_added'].str.strip()
    df_cleaned['date_added'] = pd.to_datetime(df_cleaned['date_added'], format='%B %d, %Y', errors='coerce')
    
    # Fallback for remaining null dates from parsing issues
    df_cleaned = df_cleaned.dropna(subset=['date_added'])
    
    df_cleaned['year_added'] = df_cleaned['date_added'].dt.year.astype(int)
    df_cleaned['month_added'] = df_cleaned['date_added'].dt.strftime('%B')
    df_cleaned['day_added'] = df_cleaned['date_added'].dt.strftime('%A')
    
    # 3. Standardize duration (extract numeric parts)
    # Movie: e.g. "90 min" -> 90
    # TV Show: e.g. "3 Seasons" or "1 Season" -> 3 or 1
    df_cleaned['duration_num'] = df_cleaned['duration'].apply(
        lambda x: int(str(x).split()[0]) if pd.notnull(x) else 0
    )
    df_cleaned['duration_unit'] = df_cleaned['duration'].apply(
        lambda x: str(x).split()[1] if pd.notnull(x) and len(str(x).split()) > 1 else 'min'
    )
    
    print(f"Data cleaning complete. New shape: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns")
    
    # Save clean dataset
    clean_path = os.path.join("data", "netflix_titles_cleaned.csv")
    df_cleaned.to_csv(clean_path, index=False)
    print(f"Cleaned dataset saved to: {clean_path}")
    
    return df_cleaned

def generate_visualizations(df):
    """Generate and save publication-quality visualizations answering key questions."""
    print("\n--- Phase 3: Generating Visualizations ---")
    
    # Plot 1: Content Type Distribution (Donut Chart)
    plt.figure(figsize=(7, 7))
    type_counts = df['type'].value_counts()
    colors = [NETFLIX_RED, '#564d4d']
    plt.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, 
            colors=colors, wedgeprops=dict(width=0.4, edgecolor='w'), 
            textprops={'fontsize': 13, 'weight': 'bold'})
    plt.title("Distribution of Netflix Content Types (Movies vs. TV Shows)", fontsize=16, pad=20, weight='bold')
    plt.tight_layout()
    plt.savefig("plots/content_type_distribution.png", dpi=150)
    plt.close()
    print("Saved plot: content_type_distribution.png")

    # Plot 2: Content Growth Over Time (Line Chart)
    # Filter years to exclude incomplete data (e.g. before 2008 and current year if incomplete)
    yearly_growth = df[df['year_added'] >= 2008].groupby(['year_added', 'type']).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 6))
    plt.plot(yearly_growth.index, yearly_growth['Movie'], marker='o', color=NETFLIX_RED, label='Movie', linewidth=2.5)
    plt.plot(yearly_growth.index, yearly_growth['TV Show'], marker='o', color='#564d4d', label='TV Show', linewidth=2.5)
    plt.title("Growth of Netflix Library (Content Added by Year)", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Year Added", fontsize=12)
    plt.ylabel("Number of Titles Added", fontsize=12)
    plt.xticks(yearly_growth.index, rotation=45)
    plt.legend(title="Content Type", fontsize=11)
    plt.tight_layout()
    plt.savefig("plots/release_year_trends.png", dpi=150)
    plt.close()
    print("Saved plot: release_year_trends.png")

    # Plot 3: Top 10 Countries Producing Content (Horizontal Bar Chart)
    # Split countries as some listings are co-productions
    raw_countries = df['country'].str.split(', ').dropna()
    all_countries = [country.strip() for sublist in raw_countries for country in sublist if country.strip() != 'Unknown']
    country_counts = pd.Series(all_countries).value_counts().head(10)
    
    plt.figure(figsize=(12, 7))
    sns.barplot(x=country_counts.values, y=country_counts.index, palette="Reds_r")
    plt.title("Top 10 Countries Producing Content on Netflix", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Total Titles", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/top_countries_content.png", dpi=150)
    plt.close()
    print("Saved plot: top_countries_content.png")

    # Plot 4: Content Rating Distribution (Bar Chart)
    plt.figure(figsize=(12, 6))
    rating_order = df['rating'].value_counts().index
    sns.countplot(data=df, x='rating', order=rating_order, palette="flare")
    plt.title("Content Rating Distribution on Netflix", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Rating Category", fontsize=12)
    plt.ylabel("Count of Titles", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("plots/rating_distribution.png", dpi=150)
    plt.close()
    print("Saved plot: rating_distribution.png")

    # Plot 5: Movie Duration Distribution (Histogram + KDE)
    movies_df = df[df['type'] == 'Movie']
    plt.figure(figsize=(12, 6))
    sns.histplot(data=movies_df, x='duration_num', kde=True, color=NETFLIX_RED, bins=40, alpha=0.7)
    plt.title("Distribution of Movie Durations on Netflix", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Runtime (Minutes)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    
    # Calculate statistics for annotations
    mean_len = movies_df['duration_num'].mean()
    median_len = movies_df['duration_num'].median()
    plt.axvline(mean_len, color='black', linestyle='--', label=f'Mean: {mean_len:.1f} min')
    plt.axvline(median_len, color='blue', linestyle=':', label=f'Median: {median_len:.1f} min')
    plt.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig("plots/movie_duration_distribution.png", dpi=150)
    plt.close()
    print("Saved plot: movie_duration_distribution.png")
    
    # Plot 6: Season Distribution for TV Shows (Count Plot)
    tv_df = df[df['type'] == 'TV Show']
    plt.figure(figsize=(12, 6))
    sns.countplot(data=tv_df, x='duration_num', palette="dark:red_r", order=tv_df['duration_num'].value_counts().index[:10])
    plt.title("Season Distribution of Netflix TV Shows (Top 10)", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Number of Seasons", fontsize=12)
    plt.ylabel("Count of Shows", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/tv_season_distribution.png", dpi=150)
    plt.close()
    print("Saved plot: tv_season_distribution.png")

def conduct_hypothesis_testing(df):
    """Perform simple statistical/business checks to validate hypotheses."""
    print("\n--- Phase 4: Hypothesis Testing & Insights ---")
    
    # Hypothesis 1: "Netflix has shifted its focus from Movies to TV Shows in recent years."
    # Let's check proportions in the last 5 years compared to overall.
    recent_years = df[df['year_added'] >= 2017]
    overall_ratio = df['type'].value_counts(normalize=True)
    recent_ratio = recent_years['type'].value_counts(normalize=True)
    
    print("Hypothesis 1: Focus shift from Movies to TV Shows")
    print(f"  Overall Library Ratio: Movies = {overall_ratio.get('Movie', 0)*100:.1f}%, TV Shows = {overall_ratio.get('TV Show', 0)*100:.1f}%")
    print(f"  Recent (2017+) Library Ratio: Movies = {recent_ratio.get('Movie', 0)*100:.1f}%, TV Shows = {recent_ratio.get('TV Show', 0)*100:.1f}%")
    
    # Let's count additions year by year to show trend
    yearly_ratios = df[df['year_added'] >= 2012].groupby('year_added')['type'].value_counts(normalize=True).unstack().fillna(0)
    print("\n  Yearly Additions Ratio (2012-2021):")
    for yr, row in yearly_ratios.iterrows():
        print(f"    Year {yr}: Movies = {row.get('Movie', 0)*100:.1f}%, TV Shows = {row.get('TV Show', 0)*100:.1f}%")
    
    # Hypothesis 2: "The majority of content on Netflix is rated for mature audiences (TV-MA / R)."
    mature_ratings = ['TV-MA', 'R', 'NC-17']
    mature_count = df[df['rating'].isin(mature_ratings)].shape[0]
    pct_mature = (mature_count / df.shape[0]) * 100
    print(f"\nHypothesis 2: Content classification for mature audiences")
    print(f"  Total Mature Content (TV-MA, R, NC-17): {mature_count} titles")
    print(f"  Percentage of Mature Content: {pct_mature:.1f}%")
    
    # Hypothesis 3: "Netflix's movies are typically around 90-110 minutes."
    movies_df = df[df['type'] == 'Movie']
    duration_mean = movies_df['duration_num'].mean()
    duration_median = movies_df['duration_num'].median()
    within_range = movies_df[(movies_df['duration_num'] >= 90) & (movies_df['duration_num'] <= 110)].shape[0]
    pct_range = (within_range / movies_df.shape[0]) * 100
    print(f"\nHypothesis 3: Movie duration cluster around 90-110 minutes")
    print(f"  Average Movie Duration: {duration_mean:.1f} minutes")
    print(f"  Median Movie Duration: {duration_median:.1f} minutes")
    print(f"  Percentage of Movies between 90 and 110 minutes: {pct_range:.1f}%")

def export_js_stats(df):
    """Export summary statistics as a JS file to load in frontend without CORS issues."""
    print("\n--- Phase 5: Exporting Statistics to JS ---")
    total_titles = len(df)
    movies_count = int((df['type'] == 'Movie').sum())
    movies_pct = float(movies_count / total_titles * 100)
    tv_shows_count = int((df['type'] == 'TV Show').sum())
    tv_shows_pct = float(tv_shows_count / total_titles * 100)
    
    mature_ratings = ['TV-MA', 'R', 'NC-17']
    mature_count = int(df['rating'].isin(mature_ratings).sum())
    mature_pct = float(mature_count / total_titles * 100)
    
    movies_df = df[df['type'] == 'Movie']
    avg_duration = float(movies_df['duration_num'].mean())
    median_duration = float(movies_df['duration_num'].median())
    
    unknown_director = int((df['director'] == 'Unknown Director').sum())
    unknown_cast = int((df['cast'] == 'No Cast').sum())
    unknown_country = int((df['country'] == 'Unknown').sum())
    
    js_content = f"""// Auto-generated statistics data from netflix_eda.py
const NETFLIX_STATS = {{
  totalTitles: {total_titles},
  moviesCount: {movies_count},
  moviesPct: {movies_pct:.2f},
  tvShowsCount: {tv_shows_count},
  tvShowsPct: {tv_shows_pct:.2f},
  matureCount: {mature_count},
  maturePct: {mature_pct:.2f},
  avgMovieDuration: {avg_duration:.1f},
  medianMovieDuration: {median_duration:.1f},
  missingDirectorPct: {(unknown_director / total_titles * 100):.2f},
  missingCastPct: {(unknown_cast / total_titles * 100):.2f},
  missingCountryPct: {(unknown_country / total_titles * 100):.2f}
}};
"""
    with open("plots/stats_data.js", "w") as f:
        f.write(js_content)
    print("Saved statistics file: plots/stats_data.js")

def main():
    setup_directories()
    file_path = download_dataset()
    df = load_and_explore(file_path)
    df_cleaned = clean_data(df)
    conduct_hypothesis_testing(df_cleaned)
    generate_visualizations(df_cleaned)
    export_js_stats(df_cleaned)
    print("\n--- EDA Pipeline successfully executed! All plots exported. ---")

if __name__ == "__main__":
    main()

