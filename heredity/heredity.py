import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def calculate_probability(genes, mother_genes, father_genes, trait):
    """
    Calculates the probability that a person has the trait (if trait is True),
    or does not have the trait (if trait is False),
    given the number of copies of the gene that they and their parents have.
    """
    # if no parents in dataset, use probability distribution PROBS["gene"]
    if mother_genes == None:
        # gene_prob: the probability that the person has `genes` copies of the gene
        gene_prob = PROBS["gene"][genes]

    # if parents in the dataset, each parent will pass one of their two genes on to their child randomly
    # and there is a PROBS["mutation"] chance that it mutates
    else:
        # prob_mother: the probability that the gene gets passed down from the mother
        if mother_genes == 0:
            prob_mother = PROBS["mutation"]
        elif mother_genes == 1:
            prob_mother = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
        elif mother_genes == 2:
            prob_mother = 1 - PROBS["mutation"]

        # prob_father: the probability that the gene gets passed down from the father
        if father_genes == 0:
            prob_father = PROBS["mutation"]
        elif father_genes == 1:
            prob_father = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
        elif father_genes == 2:
            prob_father = 1 - PROBS["mutation"]

        # gene_prob: the probability that the person has `genes` copies of the gene
        if genes == 0:
            gene_prob = (1 - prob_mother) * (1 - prob_father)
        elif genes == 1:
            gene_prob = (prob_mother * (1 - prob_father)) + (prob_father * (1 - prob_mother))
        elif genes == 2:
            gene_prob = prob_mother * prob_father

    trait_prob = PROBS["trait"][genes][trait]
    return gene_prob * trait_prob


def get_genes(person, one_gene, two_genes):
    if person == None:
        genes = None
    elif person in one_gene:
        genes = 1
    elif person in two_genes:
        genes = 2
    else:
        genes = 0
    return genes


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_prob = 1

    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]
        genes = get_genes(person, one_gene, two_genes)
        mother_genes = get_genes(mother, one_gene, two_genes)
        father_genes = get_genes(father, one_gene, two_genes)
        
        if person in have_trait:
            trait = True
        else:
            trait = False

        # joint probability calculated by multiplying values for individual people
        person_prob = calculate_probability(genes, mother_genes, father_genes, trait)
        joint_prob = joint_prob * person_prob

    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # update probabilities[person]["gene"] distribution
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # update probabilities[person]["trait"] distribution
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else: 
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # noramlise genes distribution
        genes_total = sum(probabilities[person]['gene'].values())
        for key in probabilities[person]['gene']:
            probabilities[person]['gene'][key] = probabilities[person]['gene'][key] / genes_total

        # normalise trait distribution
        trait_total = sum(probabilities[person]['trait'].values())
        for key in probabilities[person]['trait']:
            probabilities[person]['trait'][key] = probabilities[person]['trait'][key] / trait_total
      

if __name__ == "__main__":
    main()
