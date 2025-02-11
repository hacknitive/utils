from enum import Enum
from sys import (
    stderr,
    stdout,
)


class EnumLogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    FATAL = CRITICAL
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    WARN = WARNING
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


class EnumLogHandler(str, Enum):
    FILE = "FILE"
    CONSOLE = "CONSOLE"
    SYSLOG = "SYSLOG"


class EnumLogRotatingWhen(str, Enum):
    S = "S"  # SECONDS
    M = "M"  # MINUTES
    H = "H"  # HOURS
    D = "D"  # DAYS
    MIDNIGHT = "MIDNIGHT"  # MIDNIGHT
    W0 = "W0"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W1 = "W1"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W2 = "W2"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W3 = "W3"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W4 = "W4"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W5 = "W5"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY
    W6 = "W6"  # ROLL OVER ON A CERTAIN DAY; 0 - MONDAY


class EnumLogFacilityCode(str, Enum):
    LOG_KERN = "LOG_KERN"  # kernel messages
    LOG_USER = "LOG_USER"  # random user-level messages
    LOG_MAIL = "LOG_MAIL"  # mail system
    LOG_DAEMON = "LOG_DAEMON"  # system daemons
    LOG_AUTH = "LOG_AUTH"  # security/authorization messages
    LOG_SYSLOG = "LOG_SYSLOG"  # messages generated internally by syslogd
    LOG_LPR = "LOG_LPR"  # line printer subsystem
    LOG_NEWS = "LOG_NEWS"  # network news subsystem
    LOG_UUCP = "LOG_UUCP"  # UUCP subsystem
    LOG_CRON = "LOG_CRON"  # clock daemon
    LOG_AUTHPRIV = "LOG_AUTHPRIV"  # security/authorization messages (private)
    LOG_FTP = "LOG_FTP"  # FTP daemon
    LOG_NTP = "LOG_NTP"  # NTP subsystem
    LOG_SECURITY = "LOG_SECURITY"  # Log audit
    LOG_CONSOLE = "LOG_CONSOLE"  # Log alert
    LOG_SOLCRON = "LOG_SOLCRON"  # Scheduling daemon (Solaris)


class EnumLogSocketType(str, Enum):
    SOCK_STREAM = "SOCK_STREAM"
    SOCK_DGRAM = "SOCK_DGRAM"


class EnumLogStream(str, Enum):
    STDERR = "STDERR"
    STDOUT = "STDOUT"

STREAM_DICT = {
    EnumLogStream.STDOUT: stdout,
    EnumLogStream.STDERR: stderr,
}