# Required for running myRobogals on newer versions of macOS

import os
if os.uname()[0] == 'Darwin':
    import pymysql
    pymysql.install_as_MySQLdb()
