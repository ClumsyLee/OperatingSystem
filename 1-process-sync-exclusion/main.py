import logging
from sys import argv, exit
from threading import Thread, Semaphore
from time import sleep, time

logging.basicConfig(level=logging.WARNING)
begin_time = None
print_lock = Semaphore()

class Ticket(object):
    """Bank ticket"""
    def __init__(self, number):
        self.number = number
        self.custom = Semaphore(0)
        self.clerk = Semaphore(0)
        self.clerk_name = None

    def __str__(self):
        return str(self.number)

    def wait(self):
        self.custom.release()
        self.clerk.acquire()
        return self.clerk_name

    def call(self, clerk_name):
        self.custom.acquire()
        self.clerk_name = clerk_name
        self.clerk.release()

    def satisfied(self):
        self.custom.release()

    def serve(self):
        self.custom.acquire()

class TicketMachine(object):
    """Bank ticket machine"""
    def __init__(self, max_tickets=float('inf')):
        self.next_custom_number = 0
        self.next_clerk_number = 0
        self.tickets = []
        self.max_tickets = max_tickets

        self.available = Semaphore()

    def custom_get_ticket(self):
        self.available.acquire()

        if self.next_custom_number >= self.max_tickets:
            ticket = None  # No more tickets.
        elif self.next_custom_number >= self.next_clerk_number:
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

        if self.next_clerk_number >= self.max_tickets:
            ticket = None  # No more tickets.
        elif self.next_clerk_number >= self.next_custom_number:
            # We need a new ticket.
            ticket = Ticket(self.next_clerk_number)
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

        self.logger = logging.getLogger('Custom ' + name)

    def run(self):
        global begin_time

        sleep(self.arrive_time)
        arrive_time = time() - begin_time

        self.logger.info('Arrived, trying to get a ticket.')
        ticket = self.ticket_machine.custom_get_ticket()
        self.logger.info('Got ticket %s.', ticket)

        clerk_name = ticket.wait()

        self.logger.info('Begin to be served by Clerk %s.', clerk_name)
        serve_begin_time = time() - begin_time
        sleep(self.serve_time)

        self.logger.info('Satisfied.')
        ticket.satisfied()
        leave_time = time() - begin_time

        # Print result:
        result = '{} {:.1f} {:.1f} {:.1f} {}'.format(self.name,
                                                     arrive_time,
                                                     serve_begin_time,
                                                     leave_time,
                                                     clerk_name)
        print_lock.acquire()
        print(result)
        print_lock.release()


class Clerk(Thread):
    """Bank clerk"""
    def __init__(self, name, ticket_machine):
        super().__init__(name=name)
        self.ticket_machine = ticket_machine
        self.logger = logging.getLogger('Clerk ' + name)

    def run(self):
        while True:
            ticket = self.ticket_machine.clerk_get_ticket()
            if ticket is None:
                self.logger.info('No more customs, stop working.')
                return

            self.logger.info('Free now, assigned to ticket %s.', ticket)

            ticket.call(self.name)
            self.logger.info('Calling ticket %s.', ticket)

            self.logger.info('Serving ticket %s.', ticket)
            ticket.serve()
            self.logger.info('Done ticket %s.', ticket)

def load_customs(filename, ticket_machine):
    customs = []
    for line in open(filename):
        name, arrive_time, serve_time = line.split()
        arrive_time = float(arrive_time)
        serve_time = float(serve_time)
        customs.append(Custom(name, arrive_time, serve_time, ticket_machine))

    ticket_machine.max_tickets = len(customs)
    return customs

def load_clerks(number, ticket_machine):
    clerks = []
    for i in range(number):
        clerks.append(Clerk(str(i), ticket_machine))
    return clerks

def run(customs, clerks):
    # Record begin time.
    global begin_time
    begin_time = time()

    for custom in customs:
        custom.start()
    for clerk in clerks:
        clerk.start()

if __name__ == '__main__':
    if len(argv) != 3:
        print('Usage:', argv[0], '<input file> <clerk number>')
        exit(1)

    ticket_machine = TicketMachine()
    customs = load_customs(argv[1], ticket_machine)
    clerks = load_clerks(int(argv[2]), ticket_machine)

    run(customs, clerks)
