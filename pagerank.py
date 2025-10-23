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
    # initialize all the page probalities to zero
    # Add the newly calculated probabiity accordingly
    transition = {corpus_page: 0 for corpus_page in corpus}
    corpus_keys = corpus.keys()
    
    try:
        page_links = set(corpus[page])
    except:
        raise Exception("Page not in dictionary")
    
    # "Duplicate links on the same page are treated as a single link, 
    # and links from a page to itself are ignored as well"" 
    # This is why self-links are removed below
    if page in page_links:
        page_links.discard(page)
    

    # All links in the corpus page provided will share the damping factor probability equally
    for page_link in page_links:
        page_probability = damping_factor/len(page_links)
        transition[page_link] = transition[page_link] + page_probability

    for corpus_page in transition:
        page_probability = len(corpus_keys)/(1 - damping_factor)
        transition[corpus_page] = transition[corpus_page] + page_probability

    return transition

    # if not page_links:
    #     probability = 1/len(corpus_keys)
        
    #     for corpus_key in corpus_keys:
    #         transition[corpus_key] = corpus_key
    #     return transition

    # probability = damping_factor/selflink_check
    # for page_link in page_links:
    #     if page == page_link:
    #         continue 
    #     transition[page_link] = probability
    #     #corpus.pop(page_link)
    
    # others_probability = round((1 - damping_factor)/(len(corpus_keys) - selflink_check + 1), 5) if \
    # page in page_links else round((1 - damping_factor)/(len(corpus_keys) - selflink_check) , 5)
    
    # for corpus_key in corpus_keys:
    #     if corpus_key == page or not corpus_key in page_links:
    #         transition[corpus_key] = others_probability
    
    # #for pages, other_links in corpus.items():
    # #    if pages in transition:
    # #        continue

    # return transition


def sample_pagerank(corpus, damping_factor, n):
    """
        eturn PageRank values for each page by sampling `n` pages
        according to transition model, starting with a page at random.

        Return a dictionary where keys are page names, and values are
        their estimated PageRank value (a value between 0 and 1). All
        PageRank values should sum to 1.R
    """
    
    pages = list(corpus.keys())
    counter = {page : 0 for page in pages}

    start_page = random.choice(pages)
    outer_links = transition_model(corpus, start_page, damping_factor)
    counter[start_page] += 1

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
    
    # Here's my pseudo-algo to do this:
    # - set all of the pages ranks to (1-damping_factor)/N (for understanding this equation, look up the project question)
    # - store all the equal starting out ranks in a dictionary
    # - When calculating a new rank, check against the previous one in the dictionary 
    # - then update if new rank > prev rank + 0.001

    all_pages =  set(corpus.keys())
    all_pages_len = len(all_pages)
    pages_completed = set() # Update this set as soon as you see a page with new rank < prev rank + 0.01
    
    # Set the general starting pagerank for all pages
    page_probability = { page : (1 - damping_factor)/all_pages_len for page in all_pages }
    
    # Iteratively loop over each page setting a new page rank using the provided formula
    while True:
        for page in page_probability:
            if page in pages_completed:
                continue

            current_page_probaility = (
                ((1 - damping_factor)/all_pages_len) # First half of the formula
                + 
                damping_factor * sum([
                    page_probability[corpus_page]/(
                        len(corpus[corpus_page]) 
                        if len(corpus[corpus_page]) !=  0 else 
                        len(corpus.keys())
                    )
                    for corpus_page in corpus 
                    if page in corpus[corpus_page] or len(corpus[corpus_page]) == 0
                ]) 
                # Second half of the formula
                # The 'if' block in the list comprehension is to fulfil these conditions:
                # - "...'corpus_page' ranges over all pages that link to 'page'..."
                # -"A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself)"
            )

            if current_page_probaility <= (page_probability[page] + 0.001):
                pages_completed.add(page)
            else:
                page_probability[page] = current_page_probaility
            
        if pages_completed == all_pages:
            break

    return page_probability

    # former_probability = {}
    # current_probability = {}
    # print(corpus)

    # for page in all_pages:
    #     former_probability[page] = 1- /len(all_pages)

    # print(former_probability)
    # for _ in range(8):
    #     for page in all_pages:
    #         page_links = [link for link in corpus if page in corpus[link]]
    #         current_probability[page] = round((
    #             (1-damping_factor)/len(all_pages) + 
    #             (damping_factor * sum([former_probability[probability]/len(corpus[probability]) for probability in page_links]))
    #         ), 5)

    #         print(page, page_links, current_probability, [former_probability[probability]/len(corpus[probability]) for probability in page_links], (1-damping_factor)/len(all_pages))
    #         if (current_probability[page] - former_probability[page]) < 0.001:
    #             former_probability.pop(page)
    #         else:
    #             former_probability[page] = current_probability[page]

    #     if not former_probability:
    #         break

    # raise NotImplementedError


if __name__ == "__main__":
    main()
