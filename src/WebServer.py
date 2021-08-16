import ftplib
import paramiko


class SFTP:
    """SFTP server with class."""

    def __init__(self, host: str, login: str, pwd: str, priv_key: str) -> None:
        self.host = host
        self.username = login
        self.password = pwd
        self.path_for_priv_key = priv_key

    def __enter__(self) -> tuple:
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host,
                            username=self.username,
                            password=self.password,
                            key_filename=self.path_for_priv_key)

        self.sftp_client = self.client.open_sftp()
        return (self.client, self.sftp_client)

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.sftp_client.close()
        self.client.close()



class ServerSFTP:
    """Connects with SFTP server."""

    def __init__(self, host: str, login: str, pwd: str, priv_key: str, dir: str) -> None:
        self.host = host
        self.username = login
        self.password = pwd
        self.path_for_priv_key = priv_key
        self.dir = dir
        self.login_data = (self.host,
                           self.username,
                           self.password,
                           self.path_for_priv_key)

    def sent_file(self, file: str) -> bool:
        """Connect to SFTP server and send a file
        
        Args:
            file: path to sending file
            
        Returns:
            bool: True if succeed, False if it not
        
        """
        with SFTP(*self.login_data) as (client, sftp_client):
            try:
                sftp_client.put(file, remotepath=f'//home//{self.dir}//{file}')
                client.exec_command(f'chmod 777 //home//{self.dir}//{file}')
                return True
            except Exception:
                return False
        

    def list_of_files(self) -> list:
        """Connect to server SFTP and give back list of files in server."""

        with SFTP(*self.login_data) as (client, sftp_client):
            stdin, stdout, stderr = client.exec_command(f'ls //home//{self.dir}//')
            return [n.rstrip() for n in stdout.readlines() if '.xml' in n]


    def delete_file(self, file_name: str) -> None:
        """Deletes file form server."""

        with SFTP(*self.login_data) as (client, sftp_client):
            sftp_client.remove(f'//home//{self.dir}//{file_name}')


class ServerFTP_TLS:
    """Connects with SFTP server.
    
    Attributes:
        host: ip address of server
        login: login to server
        pwd: password to server

    """

    def __init__(self, host, login, pwd):
        self.host = host
        self.login = login
        self.pwd = pwd

    def sent_file(self, file: str) -> str:
        """Connect to FTP server and send a file.

        Args:
            file: path to sending file

        Returns:
            bool: True if succeed, False if it not:
        
        """
        with ftplib.FTP_TLS(host=self.host) as ftp:
            ftp.login(user=self.login, passwd=self.pwd)
            ftp.prot_p()
            myfile = open(file, 'rb')
            server = ftp.storlines('STOR ' + file, myfile)
            if '226' in server:
                return True
            else:
                return False

    def list_of_files(self) -> list:
        """Connect to FTP server and give back list of file on server.

        Returns:
            list: lists if file on server

        """
        with ftplib.FTP_TLS(host=self.host) as ftp:
            ftp.login(user=self.login, passwd=self.pwd)
            ftp.prot_p()
            return [x for x in ftp.nlst() if '.xml' in x]

    def delete_file(self, file_name):
        """Connect to FTP server and delete selected file.

        Args:
            str: name of file from server

        """
        with ftplib.FTP_TLS(host=self.host) as ftp:
            ftp.login(user=self.login, passwd=self.pwd)
            ftp.prot_p()
            ftp.delete(file_name)
