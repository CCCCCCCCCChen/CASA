import numpy as np
import copy
import time


def entry_count():
    FS_tw = np.zeros([72, FlightSchedule.shape[0], FlightSchedule.shape[1]])
    FlightSchedule_f_s = np.where(FlightSchedule != 0)
    for i in range(len(FlightSchedule_f_s[0])):
        f = FlightSchedule_f_s[0][i]
        s = FlightSchedule_f_s[1][i]
        t = int(FlightSchedule[f, s] // 20)
        if t < 72:
            FS_tw[t, f, s] = 1
    EntryCount = np.sum(FS_tw, axis=1)
    EntryCount = np.where((Capacity == 0), 0, EntryCount)
    return EntryCount, FS_tw


def ground_delay(FS_tw, t, s, Delay_round):
    f_in_s = np.where(FS_tw[t, :, s] == 1)[0]
    EntryTime_sort = np.array([FlightSchedule[f, s] for f in f_in_s])
    entry_order = np.argsort(EntryTime_sort)
    interval = L_time_window / Capacity[t][s]
    entry_time = copy.deepcopy(FlightSchedule[:, s])
    for i in range(len(entry_order)):
        if i == 0:
            continue
        else:
            f = f_in_s[entry_order[i]]
            f_ = f_in_s[entry_order[i - 1]]
            if entry_time[f] - entry_time[f_] < interval:
                if entry_time[f_] + interval <= L_time_window * (t + 1) - interval:
                    f_delay = entry_time[f_] + interval - entry_time[f]
                    entry_time[f] = entry_time[f_] + interval
                else:
                    f_delay = L_time_window * (t + 1) - entry_time[f]
                    entry_time[f] = L_time_window * (t + 1)

                if f_delay > Delay_round[f]:
                    Delay_round[f] = f_delay


def ground_delay_1(FS_tw, t, s, Delay_round):
    f_in_s = np.where(FS_tw[t, :, s] == 1)[0]
    EntryTime_sort = [FlightSchedule[f, s] for f in f_in_s]
    entry_order = np.argsort(EntryTime_sort)
    entry_time = copy.deepcopy(FlightSchedule[:, s])
    for i in range(int(Capacity[t][s]), len(entry_order)):
        f = f_in_s[entry_order[i]]
        f_delay = L_time_window * (t + 1) - entry_time[f]
        entry_time[f] = L_time_window * (t + 1)
        if f_delay > Delay_round[f]:
            Delay_round[f] = f_delay


def casa():

    time1 = time.time()
    EC, FS_tw = entry_count()
    N_HotSpot = np.where(EC > Capacity, 1, 0).sum()
    Delay_total = np.zeros(N_flight)

    round_n = 0
    while N_HotSpot > 0:
        N_HotSpot = 0
        Delay_round = np.zeros(N_flight)
        for s in range(N_sector):
            for t in range(N_time_window):
                if EC[t, s] > Capacity[t, s]:
                    N_HotSpot += 1
                    ground_delay(FS_tw, t, s, Delay_round)

        for f in range(N_flight):
            if Delay_round[f] != 0:
                for s in range(N_sector):
                    if FlightSchedule[f][s] != 0:
                        t = int(FlightSchedule[f][s] // L_time_window)
                        t_ = int((FlightSchedule[f][s] + Delay_round[f]) // L_time_window)
                        if t < t_ and t < N_time_window:
                            FS_tw[t, f, s] = 0
                            if Capacity[t, s] != 0:
                                EC[t, s] -= 1
                            if t_ < N_time_window:
                                FS_tw[t_, f, s] = 1
                                if Capacity[t_, s] != 0:
                                    EC[t_, s] += 1
                        FlightSchedule[f][s] += Delay_round[f]

        Delay_total += Delay_round
        print('round', round_n, ', number of HotSpot', N_HotSpot,
              ', round delay flight', np.count_nonzero(Delay_round),
              ', round delay time', round(Delay_round.sum()), ', total delay flight',
              np.count_nonzero(Delay_total), ', total delay time', round(Delay_total.sum()))
        round_n += 1

    time2 = time.time()
    print('calculating time', time2 - time1)


if __name__ == "__main__":

    N_time_window = 72
    L_time_window = 1440 / N_time_window

    FlightSchedule = ...
    """
    *FlightSchedule* should be a np.array whose dimension is [num_flights, num_sector]. 
    An element of it means that the flight's entry time into the sector.
    """
    Capacity = ...
    """
    *Capacity* should be a np.array whose dimension is [num_time_window, num_sector].
    An element of it means that the capacity of the sector in the time window.
    """

    N_flight = FlightSchedule.shape[0]
    N_sector = FlightSchedule.shape[1]

    casa()





