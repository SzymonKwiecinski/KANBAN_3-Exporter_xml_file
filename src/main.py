from MainWindow import *
from SQLServerConnection import *
from WebServer import ServerFTP_TLS, ServerSFTP

if __name__ == '__main__':
    MainWindow(ms_sql=SQLServerConnection(),
               web_server=ServerSFTP(host='00.000.000.00',
                                     login='login',
                                     pwd='password',
                                     priv_key='path_to_ssh_hey',
                                     dir='name_of_diretory_on_server'),
               history_file='..//archive//history.csv',
               error_file='..//archive//error.csv',
               pr_error_file='..//archive//programming_errors.txt',
               old_files='..//old_file//')
