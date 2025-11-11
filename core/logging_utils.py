from loguru import logger
from sqlalchemy.orm import Session
from core.models import ProposalLog

class DBLogHandler:
    def __init__(self, session: Session, reference_no: str | None = None, proposal_id: int | None = None):
        self.session = session
        self.reference_no = reference_no
        self.proposal_id = proposal_id

    def write(self, message):
        # loguru sends formatted string lines ending with "\n"
        msg = message.strip()
        if not msg:
            return
        log = ProposalLog(
            proposal_id=self.proposal_id,
            reference_no=self.reference_no,
            message=msg,
        )
        self.session.add(log)

    def flush(self):
        self.session.flush()

def attach_db_sink(session: Session, reference_no: str | None, proposal_id: int | None):
    handler = DBLogHandler(session, reference_no, proposal_id)
    sink_id = logger.add(handler, level="INFO")
    return sink_id
