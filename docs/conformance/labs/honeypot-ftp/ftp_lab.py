#!/usr/bin/env python3
"""Plain-FTP lab entry (SSL omitted). UHBS compatibility shim."""

import os
import sys
import time
import uuid

from twisted.python import filepath
from twisted.protocols.ftp import FTP, FTPFactory, FTPRealm
from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB
from twisted.internet import reactor

from base.applog import log
from base.appconfig import Configuration
from handler.manager import HandlerManager


class FTPConfig(Configuration):
    def setup(self, *args, **kwargs):
        self.port = int(os.environ.get("FTP_PORT", "21"))
        self.pubdir = os.environ.get("FTP_PUBDIR", "pub/")
        self.passwdfile = os.environ.get("FTP_PASSWD", "passwd")


config = FTPConfig()
handler = HandlerManager(config)


class MyFTPRealm(FTPRealm):
    def __init__(self, directory):
        self.userHome = filepath.FilePath(directory)

    def getHomeDirectory(self, avatarId):
        return self.userHome


class SimpleFtpProtocol(FTP):
    def __init__(self):
        self.session = str(uuid.uuid1())
        self.myownhost = None

    def connectionMade(self):
        self.__logInfo("connected", "", True)
        FTP.connectionMade(self)

    def connectionLost(self, reason):
        self.__logInfo("disconnected", "", True)
        FTP.connectionLost(self, reason)

    def lineReceived(self, line):
        self.__logInfo("command", line, True)
        FTP.lineReceived(self, line)

    def ftp_STOR(self, path):
        FTP.sendLine(self, b"125 Data connection already open, starting transfer")
        FTP.sendLine(self, b"226 Transfer Complete.")

    def ftp_DELE(self, path):
        FTP.sendLine(self, b"250 Requested File Action Completed OK")

    def ftp_RNFR(self, fromName):
        FTP.sendLine(self, b"350 Requested file action pending further information.")

    def ftp_RNTO(self, toName):
        FTP.sendLine(self, b"250 Requested File Action Completed OK")

    def ftp_MKD(self, path):
        FTP.sendLine(self, b"257 Folder created")

    def ftp_RMD(self, path):
        FTP.sendLine(self, b"250 Requested File Action Completed OK")

    def __logInfo(self, type, command, successful):
        try:
            self.myownhost = self.transport.getHost()
        except AttributeError:
            pass
        data = {
            "module": "FTP",
            "@timestamp": int(time.time() * 1000),
            "sourceIPv4Address": str(self.transport.getPeer().host),
            "sourceTransportPort": self.transport.getPeer().port,
            "type": type,
            "command": str(command),
            "success": successful,
            "session": self.session,
        }
        if self.myownhost:
            data["destinationIPv4Address"] = str(self.myownhost.host)
            data["destinationTransportPort"] = self.myownhost.port
        handler.handle(data)


def main() -> int:
    os.makedirs(config.pubdir, exist_ok=True)
    factory = FTPFactory(
        Portal(MyFTPRealm(config.pubdir)),
        [FilePasswordDB(config.passwdfile)],
    )
    factory.protocol = SimpleFtpProtocol
    reactor.listenTCP(config.port, factory)
    log.info("Server listening on Port %s (Plain FTP lab)." % (config.port,))
    reactor.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
