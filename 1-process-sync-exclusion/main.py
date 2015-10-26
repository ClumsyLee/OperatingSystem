import logging
from threading import Thread, Semaphore
from time import sleep

logging.basicConfig(level=logging.INFO)

class Ticket(object):
    """Bank ticket"""
    def __init__(self, number):
        self.number = number
        self.custom = Semaphore(0)
        self.clerk = Semaphore(0)

    def __str__(self):
        return str(self.number)

    def wait(self):
        self.custom.release()

    def call(self):
        self.custom.acquire()
        self.clerk.release()

    def sit(self):
        self.clerk.acquire()

    def satisfied(self):
        self.custom.release()

    def serve(self):
        self.custom.acquire()

class TicketMachine(object):
    """Bank ticket machine"""
    def __init__(self):
        self.next_custom_number = 0
        self.next_clerk_number = 0
        self.tickets = []

        self.available = Semaphore()

    def custom_get_ticket(self):
        self.available.acquire()

        if self.next_custom_number >= self.next_clerk_number:
            # We need a new ticket.
            ticket = Ticket(self.next_custom_number)
            self.tickets.append(ticket)
        else:
            # The ticket already exists.
            ticket = self.tickets[self.next_custom_number]
        self.next_custom_number += 1

        self.available.release()  # Make self available.
        return ticket

    def clerk_get_ticket(self):
        self.available.acquire()

        if self.next_clerk_number >= self.next_custom_number:
            # We need a new ticket.
            ticket = Ticket(self.next_custom_number)
            self.tickets.append(ticket)
        else:
            # The ticket already exists.
            ticket = self.tickets[self.next_clerk_number]
        self.next_clerk_number += 1

        self.available.release()  # Make self available.
        return ticket

class Custom(Thread):
    """Bank custom"""
    def __init__(self, name, arrive_time, serve_time, ticket_machine):
        super().__init__(name=name)
        self.arrive_time = arrive_time
        self.serve_time = serve_time
        self.ticket_machine = ticket_machine

        self.logger = logging.getLogger('Custom.' + name)

    def run(self):
        sleep(self.arrive_time)

        self.logger.info('Arrived, trying to get a ticket.')
        ticket = self.ticket_machine.custom_get_ticket()
        self.logger.info('Got ticket %s.', ticket)

        ticket.wait()
        ticket.sit()

        self.logger.info('Begin to be served.')
        sleep(self.serve_time)

        self.logger.info('Satisfied.')
        ticket.satisfied()

class Clerk(Thread):
    """Bank clerk"""
    def __init__(self, name, ticket_machine):
        super().__init__(name=name)
        self.ticket_machine = ticket_machine
        self.logger = logging.getLogger('Clerk.' + name)

    def run(self):
        while True:
            ticket = self.ticket_machine.clerk_get_ticket()
            self.logger.info('Free now, assigned to ticket %s.', ticket)

            ticket.call()
            self.logger.info('Calling ticket %s.', ticket)

            self.logger.info('Serving ticket %s.', ticket)
            ticket.serve()
            self.logger.info('Done ticket %s.', ticket)

if __name__ == '__main__':
    ticket_machine = TicketMachine()
    Custom('1', 1, 10, ticket_machine).start()
    Custom('2', 5, 2, ticket_machine).start()
    Custom('3', 6, 3, ticket_machine).start()
    Clerk('1', ticket_machine).start()
