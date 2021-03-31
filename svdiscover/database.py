import sqlite3

class DatabaseHandler():
    """IMPORTANT NOTE: Don't use this code in production without cleaning inputs!
    Sets up a SQLite database connection with simple functions.
    Decorator reference: https://stackoverflow.com/questions/1263451/python-decorators-in-classes  
    
    Args:
        db_root (string): Path to the database. 
    """
    def __init__(self, db_root):
        self.db = sqlite3.connect(db_root)
        self.cursor = self.db.cursor()
        self.table = None

    def _table_selected(func):
        """Checks if self.table has been set for functions that require selecting a table
        
        Arguments:
            func {Method} -- Function that uses table as input
        """            
        def inner(self, *args, **kwargs):
            if not self.table:
                raise AssertionError("No table selected. Set a table by setting [db_name].table")
            else:
                return func(self, *args, **kwargs)
        return inner

    def execute_cmd(self, command_str, manual_commit=False):
        """Catch-all method for manually running commands
        
        Arguments:
            command_str {str} -- String with SQL instructions
        
        Keyword Arguments:
            manual_commit {bool} -- Commit after completing (default: {False})
        """        
        try:
            self.cursor.execute(command_str)
            if not manual_commit:
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    @_table_selected
    def remove_records(self, where_clause=False):
        """Remove records from the target table
        
        Keyword Arguments:
            where_clause {str} -- Optional where clause to limit deletion
        """        
        try:
            if where_clause:
                self.db.execute(f'DELETE FROM {self.table} WHERE {where_clause}')
            else:
                self.db.execute(f'DELETE * FROM {self.table}')
            self.db.commit()
        except sqlite3.IntegrityError as e:
            print(f'Cannot delete record: {e}')
    
    @_table_selected
    def get_records(self, where_clause=None):
        """Select records from the target table
        
        Keyword Arguments:
            where_clause {str} -- Optional where clause to limit selection (default: {None})
        
        Returns:
            {list} -- List of lists containing all selected records
        """        
        try:
            if where_clause:
                records = [record for record in self.cursor.execute(f'SELECT * FROM {self.table} WHERE {where_clause}')]
            else:
                records = [record for record in self.cursor.execute(f'SELECT * FROM {self.table}')]
            return records
        except sqlite3.IntegrityError as e:
            print(f'Cannot load records: {e}')
    
    @_table_selected
    def add_field(self, field_name, datatype):
        """Adds a field to the target table
        
        Arguments:
            field_name {str} -- Name of the new field
            datatype {str} -- String of field's datatype in SQL syntax
        """        
        try:
            self.db.execute(f'ALTER TABLE {self.table} ADD COLUMN {field_name} {datatype};')
        except sqlite3.IntegrityError as e:
            self.db.rollback()
            print(f'Cannot add field: {e}')

    _table_selected = staticmethod(_table_selected)

class StreetviewDB(DatabaseHandler):
    def __init__(self, db_root):
        super().__init__(db_root)

    def make_region_table(self, table_name, set_target=False):
        """Makes a table to store streetview panorama information for a given region
        
        Arguments:
            table_name {str} -- Name of the new region table
        
        Keyword Arguments:
            set_target {bool} -- Make this table the target table for future functions? (default: {False})
        """        
        self.execute_cmd(f'''CREATE TABLE IF NOT EXISTS {table_name}
                                (subregion_name VARCHAR,
                                pano_id VARCHAR,
                                capture_date VARCHAR,
                                anchor_x REAL,
                                anchor_y REAL,
                                pano_x REAL,
                                pano_y REAL,
                                lookup_date VARCHAR,
                                download_date VARCHAR,
                                saved_path VARCHAR,
                                PRIMARY KEY (pano_id, subregion_name)
                                )''')
        if set_target:
            self.table = table_name

    @DatabaseHandler._table_selected
    def add_entry(self, entry, manual_commit=False):
        """Stores a record in the target table
        
        Arguments:
            entry {dict} -- dictionary containing entries for all table fields
        
        Keyword Arguments:
            manual_commit {bool} -- Commit after completing (default: {False})
        """            
        try:
            self.cursor.execute(f'INSERT INTO {self.table} VALUES (?,?,?,?,?,?,?,?,?,?)',
                                    [
                                        entry['subregion_name'],
                                        entry['pano_id'],
                                        entry['capture_date'],
                                        entry['anchor_x'],
                                        entry['anchor_y'],
                                        entry['pano_x'],
                                        entry['pano_y'],
                                        entry['lookup_date'],
                                        entry['download_date'],
                                        entry['saved_path']
                                    ]
                            )
            if not manual_commit:
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            if 'UNIQUE constraint failed' in str(e):
                print(f'Duplicate entry for pano {entry["pano_id"]} ignored.')
            else:
                raise e

    # def calculate_splits(self, table, field_name, split_probabilities, commit_interval=50):
    #     records = self.get_all_records(table)
    #     for i, record in enumerate(records):
    #         split = determine_split(split_probabilities)
    #         try:
    #             self.db.execute(f'UPDATE {table} SET {field_name}=(?) WHERE img_id=(?)', [split, record[0]])
    #             if i % commit_interval == 0 or i == len(records):
    #                 self.db.commit()
    #         except sqlite3.IntegrityError as e:
    #             print(f'Cannot load records: {e}')