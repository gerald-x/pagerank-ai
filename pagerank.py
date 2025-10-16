import os
import random
import re
import sys

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
    transition = {}
    corpus_keys = corpus.keys()
    try:
        page_links = corpus[page]
    except:
        raise Exception("Page not in dictionary")
    
    selflink_check = len(page_links)-1 if page in page_links else len(page_links)
    
    if not page_links or not selflink_check:
        probability = 1/len(corpus_keys)
        for corpus_key in corpus_keys:
            transition[corpus_key] = corpus_key
        return transition

    probability = damping_factor/selflink_check
    for page_link in page_links:
        if page == page_link:
            continue 
        transition[page_link] = probability
        #corpus.pop(page_link)
    
    others_probability = round((1 - damping_factor)/(len(corpus_keys) - selflink_check + 1), 5) if \
    page in page_links else round((1 - damping_factor)/(len(corpus_keys) - selflink_check) , 5)
    
    for corpus_key in corpus_keys:
        if corpus_key == page or not corpus_key in page_links:
            transition[corpus_key] = others_probability
    
    #for pages, other_links in corpus.items():
    #    if pages in transition:
    #        continue

    return transition


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    counter = {}
    for page in pages:
        counter[page] = 0
    
    start_page = random.choice(pages)
    outer_links = transition_model(corpus, start_page, damping_factor)
    counter[start_page] += 1

    print(start_page, outer_links)
    for _ in range(n-1):
        start_page = random.choices(list(outer_links.keys()), list(outer_links.values()), k=1)[0]
        outer_links = transition_model(corpus, start_page, damping_factor)
        counter[start_page] += 1

    for counter_key in counter:
        counter[counter_key] = counter[counter_key]/n

    return counter


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    print("==================================================\nIterative Debugging")
    all_pages =  set(corpus.keys())
    former_probability = {}
    current_probability = {}
    print(corpus)

    for page in all_pages:
        former_probability[page] = 1/len(all_pages)

    print(former_probability)
    for _ in range(8):
        for page in all_pages:
            page_links = [link for link in corpus if page in corpus[link]]
            current_probability[page] = round((
                (1-damping_factor)/len(all_pages) + 
                (damping_factor * sum([former_probability[probability]/len(corpus[probability]) for probability in page_links]))
            ), 5)

            print(page, page_links, current_probability, [former_probability[probability]/len(corpus[probability]) for probability in page_links], (1-damping_factor)/len(all_pages))
            if (current_probability[page] - former_probability[page]) < 0.001:
                former_probability.pop(page)
            else:
                former_probability[page] = current_probability[page]

        if not former_probability:
            break

    #print(all_pages, "\n", current_probability)

    
    raise NotImplementedError


if __name__ == "__main__":
    main()
