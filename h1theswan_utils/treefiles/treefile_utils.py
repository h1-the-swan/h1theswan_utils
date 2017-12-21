import pandas as pd
import numpy as np

class Treefile(object):

    """Tools for working with a treefile (.tree)"""

    def __init__(self,
                fname=None,
                comment_char="#",
                field_sep=" ",
                cluster_sep=":"):
        """
        :fname: filename for the treefile
        """

        self.fname = fname
        self.comment_char = comment_char
        self.field_sep = field_sep
        self.cluster_sep = cluster_sep

        self.d = None

    def parse(self, fname=None):
        """Parse the treefile

        :fname: filename for the treefile
        :returns: list of dictionaries. each item in the list is a row in the treefile

        """

        if fname is not None:
            self.fname = fname
        else:
            fname = self.fname

        d = []
        with open(fname, 'r') as f:
            for line in f:
                if line[0] == self.comment_char:
                    continue
                line = line.strip().split(self.field_sep)
                this_row = {}
                this_row['path'] = line[0]
                this_row['flow'] = float(line[1])
                this_row['name'] = line[2].strip('"')
                if len(line) > 3:
                    this_row['node'] = int(line[3])
                d.append(this_row)
        self.d = d

    def load_df(self):
        """load treefile as a pandas dataframe
        :returns: pandas dataframe

        """
        if not self.d:
            self.parse()

        self.df = pd.DataFrame(self.d)
        return self.df
        
