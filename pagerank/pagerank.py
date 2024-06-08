import os
import random
import re
import sys
import numpy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    page_links = corpus[page]
    page_probs = dict()
    # if page has no outgoing links, return a probability distribution that chooses randomly among all pages with equal probability
    if len(page_links) == 0:
        for page in corpus:
            page_probs[page] = 1 / len(corpus)
    else:
        for page in corpus:
            # With probability 1 - damping_factor, the random surfer should randomly choose one of all pages in the corpus with equal probability
            prob = (1 - damping_factor) / len(corpus)
            if page in page_links:
                # With probability damping_factor, the random surfer should randomly choose one of the links from page with equal probability
                prob  = prob + damping_factor / len(page_links)
            page_probs[page] = prob
    return page_probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    # keep track of how many times each page has been visited (initially 0)
    page_visits = {page: 0 for page in pages}
    # first sample: choose from a page at random
    sample = random.choice(pages)
    page_visits[sample] = 1
    # remaining samples: generate from previous sample using transition model
    for i in range(1, n):
        sample_trans_model = transition_model(corpus=corpus, page=sample, damping_factor=damping_factor)
        options = list(sample_trans_model.keys())
        option_probs = list(sample_trans_model.values())
        sample = numpy.random.choice(options, p=option_probs)
        page_visits[sample] += 1

    # proportion of all the samples that corresponded to that page
    pageranks = {k: v / n for k, v in page_visits.items()}
    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    # start by assuming equally likely to be on any page
    pageranks = {page: 1 / len(pages) for page in pages}

    # iteratively calculate new rank values using PageRank formula
    # until no PageRank value changes by more than 0.001
    max_pagerank_diff = numpy.inf
    old_pageranks = pageranks
    while max_pagerank_diff > 0.001:
        new_pageranks = {page: pagerank(page, corpus, old_pageranks, damping_factor) for page in pages}
        max_pagerank_diff = 0
        for i in pages:
            pagerank_diff = new_pageranks[i] - old_pageranks[i]
            if pagerank_diff > max_pagerank_diff:
                max_pagerank_diff = pagerank_diff
        old_pageranks = new_pageranks
    return new_pageranks


def pagerank(page, corpus, pageranks, damping_factor):
    """
    Return the PageRank of a given page,
    the probability that a random surfer ends up on that page
    """
    prob_link_followed = 0  # probability surfer followed a link to the given page
    for i in corpus:
        # interpret a page with no links as having 1 link for every page in the corpus 
        if len(corpus[i]) == 0:
            pagerank_i = pageranks[i]
            prob_link_followed += (pagerank_i / len(corpus))
        # sum over each page i that links to page: pagerank of i / number of links on i
        elif page in corpus[i]:
            pagerank_i = pageranks[i]
            links_i = len(corpus[i])
            prob_link_followed += (pagerank_i / links_i)

    new_pagerank = ((1-damping_factor) / len(corpus)) + (damping_factor * prob_link_followed)
    return new_pagerank


if __name__ == "__main__":
    main()
