import feedparser
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os
import tkinter as tk
from tkinter import messagebox


nltk.download('punkt')
nltk.download('stopwords')

def get_feed_entries(feed_url):
    feed = feedparser.parse(feed_url)
    entries = feed.entries
    return entries

def summarize_text(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Frequency table
    freq_table = dict()
    for word in words:
        word = word.lower()
        if word not in stop_words:
            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1

    sentences = sent_tokenize(text)

    # Score sentences based on frequency
    sentence_value = dict()
    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq

    # Average score for sentences
    sum_values = 0
    for sentence in sentence_value:
        sum_values += sentence_value[sentence]

    average = int(sum_values / len(sentence_value))

    # Get the summary
    summary = ''
    for sentence in sentences:
        if (sentence in sentence_value) and (sentence_value[sentence] > (1.5 * average)):
            summary += " " + sentence
    return summary

def write_to_file(file_path, read_articles):
    with open(file_path, 'w') as f:
        for article_id in read_articles:
            f.write(f"{article_id}\n")

def read_articles_from_file(file_path):
    if not os.path.exists(file_path):
        return set()

    with open(file_path, 'r') as f:
        read_articles = f.readlines()

    # Remove newline character from each line
    read_articles = {article_id.strip() for article_id in read_articles}
    return read_articles

def get_arxiv_updates():
    read_articles = read_articles_from_file('read_articles.txt')
    interesting_articles = read_articles_from_file('interesting_articles.txt')
    
    feed_url = 'http://export.arxiv.org/rss/cs.AI'  # RSS feed URL for arXiv Artificial Intelligence category
    entries = get_feed_entries(feed_url)

    root = tk.Tk()
    root.withdraw()
    
    for entry in entries:
        if entry.id not in read_articles:
            summary = summarize_text(entry.summary)
            if summary != '':
                messagebox.showinfo(f"Title: {entry.title}", f"Summary: {summary}\n")
                user_input = messagebox.askyesno("Confirmation", "Is the article interesting?")
                if user_input == 'no':
                    read_articles.add(entry.id)
                else:
                    interesting_articles.add(entry.id)
                    user_input = messagebox.askyesno("Confirmation", "Do you want to see it next time?")
                    if user_input == 'no':
                        read_articles.add(entry.id)
                                   
            else:
                read_articles.add(entry.id)

    
    # Write the updated set of read articles back to the file
    write_to_file('read_articles.txt', read_articles)
    write_to_file('interesting_articles.txt', interesting_articles)

    root.destroy()
        
get_arxiv_updates()
