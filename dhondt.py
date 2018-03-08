import heapq

from collections import namedtuple
from itertools import groupby

Group = namedtuple('Group', 'quotient seats_won candidates group records')


class Dhondt:
    def __init__(self, group_key_list, votes_key, seats, records):
        self.winners = []
        self.losers = []
        self._calculate(group_key_list, votes_key, seats, records)

    def _calculate(self, group_key_list, votes_key, seats, records):
        current_group = group_key_list[0]
        if len(group_key_list) > 1:
            remainder_group_list = group_key_list[1:]
        else:
            remainder_group_list = None

        heap = self._generate_heap(current_group, votes_key, records)

        if heap:
            heap = self._allocate_seats(
                current_group,
                votes_key,
                heap,
                seats)
            if remainder_group_list is not None:
                for group in heap:
                    self._calculate(
                        remainder_group_list,
                        votes_key,
                        group.seats_won,
                        group.records)
            else:
                self._assign_seats(heap, votes_key)

    def _generate_heap(self, group_key, votes_key, records):
        heap = []
        srtd_records = sorted(records, key=lambda r: r[group_key])
        for key, records in groupby(srtd_records, key=lambda r: r[group_key]):
            records = list(sorted(records, key=lambda r: r[votes_key]))
            heapq.heappush(heap, Group(
                quotient=-sum(int(r[votes_key]) for r in records),
                seats_won=0,
                candidates=len(records),
                group=key,
                records=records
            ))

        return heap

    def _allocate_seats(self, group_key, votes_key, heap, seats):
        for seat in range(seats):
            group = heapq.heappop(heap)
            if group.quotient == 0:
                heapq.heappush(heap, group)
                break

            seats_won = group.seats_won + 1
            if group.seats_won < group.candidates:
                quotient = group.quotient * seats_won / (seats_won + 1)
            else:
                quotient = 0
            heapq.heappush(
                heap,
                Group(
                    quotient=quotient,
                    seats_won=seats_won,
                    candidates=group.candidates,
                    group=group.group,
                    records=group.records))

        return heap

    def _assign_seats(self, heap, votes_key):
        for group in heap:
            srtd_records = sorted(group.records,
                                  key=lambda r: int(r[votes_key]))
            for seated in range(group.seats_won):
                self.winners.append(srtd_records.pop())
            for notseated in range(len(srtd_records)):
                self.losers.append(srtd_records.pop())
