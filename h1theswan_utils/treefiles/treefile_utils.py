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
        self.df = None
        self.top_cluster_counts = None

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

    def add_top_cluster_column_to_df(self, df=None):
        df = df or self.df
        if df is None:
            raise RuntimeError("df is not specified. call load_df() to load the dataframe")
        top_cluster = df['path'].apply(lambda x: x.split(self.cluster_sep)[0])
        top_cluster.name = 'top_cluster'
        df['top_cluster'] = top_cluster
        return df
        
    def top_cluster_counts(self, df=None):
        df = df or self.df
        if df is None:  # if it's still not there, load it (parsing the treefile if necessary)
            df = self.load_df()
        
        df = self.add_top_cluster_column_to_df(df=df)
        self.top_cluster_counts = df['top_cluster'].value_counts()
        return self.top_cluster_counts

