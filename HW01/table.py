import sys
import os
import re

class Processor():
    
    def __init__(self,
                 ignore: list=None,
                 words: list=None,
                 blanks: list=None,
                 keywords: list=None
                 )->None:
        self.ignore = ignore
        self.words = words
        self.blanks = blanks
        self.keywords = keywords
        
        return
    
    def tokenize(self,
                 s: str=None
                 )->str:
        '''
        
        Tokenize input.txt converted to string according to tokenization rules.
            
            s:
                <str>:
                    the string of raw text to be tokenized

        Returns a list of tokens, i.e., a <list> of <str>

        '''
        # 1.    Anything on a line after the character “#” is ignored.
        s = re.sub(pattern = r"#.+\n",
                   repl = "",
                   string=s
                   )
        tokens = []
        word = []
        for char in s:

            # WORDS -- > starts with a letter or an underscore (no digits)
            if re.match(r'[A-Za-z_]', char) and not word:   
                word.append(char)
            elif re.match(r'[0-9]', char) and not word:
                print('WARNING: encountered word starting with a digit')
            
            # WORDS --> any sequence of (one or more) consecutive letters, digits, or underscores
            elif re.match(r'[A-Za-z_0-9]', char) and word:
                word.append(char)
            
            # BLANKS --> spaces, tabs, carriage, newlines markd the end of a word
            elif re.match(r'[\s]', char) and word:  # [\s] == [\t\n\r' ']
                tokens.append(''.join(word))
                word = []
            
            # SPECIAL chars
            elif re.match(r'[()=;]', char):
                if word:    # special char ends a word
                    tokens.append(''.join(word))
                    word = []
                tokens.append(char)

        return tokens
    
    def parse(self,
              tokens: list=None
        )->None:
        """
        
        Parses the input according to parsing rules. Yields Variable Declarations, Assignments and Show Instructions.

            tokens:
                <list>:
                    a list of valid tokens.
        Returns

        """
        
        pass

processor = Processor()

with open(sys.argv[1], 'r') as f:
    
    f = f.read()
    
    print("-"*30)
    print(f"Input of type {type(f)}:")
    print("-"*30)
    print(f)
    
    f = processor.tokenize(f)

    print("-"*30)
    print(f'Tokenized Input:')
    print("-"*30)
    print(f)