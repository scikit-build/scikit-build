
#cython: boundscheck=False
#cython: cdivision=True
#cython: cdivision_warnings=True
#cython: profile=True

from libc.math cimport sin, cos

cdef class Pen2Sim:
    cdef:
        double th0, th1, w0, w1
        double M0, M1, L0, L1, G, dt, t
        double th0_dot, th1_dot, w0_dot, w1_dot

        double U_th0, U_th1, U_w0, U_w1
        double k0_th0, k0_th1, k0_w0, k0_w1
        double k1_th0, k1_th1, k1_w0, k1_w1
        double k2_th0, k2_th1, k2_w0, k2_w1
        double k3_th0, k3_th1, k3_w0, k3_w1

        double Ix0, Ix1, Iy0, Iy1, Ith0, Ith1

    def __init__(self, double th0, double th1,
                       double w0, double w1,
                       double M0, double M1,
                       double L0, double L1,
                       double G, double dt):
        self.th0 = th0
        self.th1 = th1
        self.w0 = w0
        self.w1 = w1
        self.M0 = M0
        self.M1 = M1
        self.L0 = L0
        self.L1 = L1
        self.G = G
        self.dt = dt
        self.t = 0.0

        self.Ith0 = self.th0
        self.Ith1 = self.th1

        self.Ix0 = self.L0*sin(self.Ith0)
        self.Ix1 = self.Ix0 + self.L1*sin(self.Ith1)

        self.Iy0 = -self.L0*cos(self.Ith0)
        self.Iy1 = self.Iy0 - self.L1*cos(self.Ith1)

    def initial_state(self):
        return (self.Ix0, self.Ix1, self.Iy0, self.Iy1, 0.0, self.L0, self.L1, self.Ith0, self.Ith1)

    cdef void eval_rhs(self):
        cdef:
            double th0 = self.U_th0
            double th1 = self.U_th1
            double w0  = self.U_w0
            double w1  = self.U_w1
            double M0  = self.M0
            double M1  = self.M1
            double L0  = self.L0
            double L1  = self.L1
            double G   = self.G

        self.th0_dot = w0
        self.th1_dot = w1

        self.w0_dot = -(
            4.0*G *M0        *sin(    th0          )
          + 3.0*G *M1        *sin(    th0          )
          +     G *M1        *sin(    th0 - 2.0*th1)
          +     L0*M1*(w0**2)*sin(2.0*th0 - 2.0*th1)
          + 4.0*L1*M1*(w1**2)*sin(    th0 -     th1)
        )/(
            2.0*L0*(4.0*M0 - M1*cos(th0 - th1)**2 + 2.0*M1)
        )

        self.w1_dot = (
           -(2.0*M0 + M1)*(
                G         *sin(      th1)
              - L0*(w0**2)*sin(th0 - th1)
            )

          + cos(th0 - th1)*(
                G *M0        *sin(th0      )
              + G *M1        *sin(th0      )
              + L1*M1*(w1**2)*sin(th0 - th1)
            )
        )/(
            L1*(
                4.0*M0
              -     M1*cos(th0 - th1)**2
              + 2.0*M1
            )
        )

    cdef simulate(self):
        # classical runge-kutta
        self.U_th0 = self.th0
        self.U_th1 = self.th1
        self.U_w0 = self.w0
        self.U_w1 = self.w1
        self.eval_rhs()
        self.k0_th0 = self.th0_dot
        self.k0_th1 = self.th1_dot
        self.k0_w0 = self.w0_dot
        self.k0_w1 = self.w1_dot

        self.U_th0 = self.th0 + 0.5*self.dt*self.k0_th0
        self.U_th1 = self.th1 + 0.5*self.dt*self.k0_th1
        self.U_w0 = self.w0   + 0.5*self.dt*self.k0_w0
        self.U_w1 = self.w1   + 0.5*self.dt*self.k0_w1
        self.eval_rhs()
        self.k1_th0 = self.th0_dot
        self.k1_th1 = self.th1_dot
        self.k1_w0 = self.w0_dot
        self.k1_w1 = self.w1_dot

        self.U_th0 = self.th0 + 0.5*self.dt*self.k1_th0
        self.U_th1 = self.th1 + 0.5*self.dt*self.k1_th1
        self.U_w0 = self.w0   + 0.5*self.dt*self.k1_w0
        self.U_w1 = self.w1   + 0.5*self.dt*self.k1_w1
        self.eval_rhs()
        self.k2_th0 = self.th0_dot
        self.k2_th1 = self.th1_dot
        self.k2_w0 = self.w0_dot
        self.k2_w1 = self.w1_dot

        self.U_th0 = self.th0 + self.dt*self.k2_th0
        self.U_th1 = self.th1 + self.dt*self.k2_th1
        self.U_w0 = self.w0   + self.dt*self.k2_w0
        self.U_w1 = self.w1   + self.dt*self.k2_w1
        self.eval_rhs()
        self.k3_th0 = self.th0_dot
        self.k3_th1 = self.th1_dot
        self.k3_w0 = self.w0_dot
        self.k3_w1 = self.w1_dot

        cdef double dth0, dth1, dw0, dw1
        dth0 = self.k0_th0 + 2.0*(self.k1_th0 + self.k2_th0) + self.k3_th0
        dth1 = self.k0_th1 + 2.0*(self.k1_th1 + self.k2_th1) + self.k3_th1
        dw0  = self.k0_w0  + 2.0*(self.k1_w0  + self.k2_w0 ) + self.k3_w0
        dw1  = self.k0_w1  + 2.0*(self.k1_w1  + self.k2_w1 ) + self.k3_w1

        dth0 *= self.dt
        dth1 *= self.dt
        dw0  *= self.dt
        dw1  *= self.dt

        dth0 /= 6.0
        dth1 /= 6.0
        dw0  /= 6.0
        dw1  /= 6.0

        self.th0 += dth0
        self.th1 += dth1
        self.w0  += dw0
        self.w1  += dw1

        self.t += self.dt

        cdef double x0, x1, y0, y1

        x0 = self.L0*sin(self.th0)
        x1 = x0 + self.L1*sin(self.th1)

        y0 = -self.L0*cos(self.th0)
        y1 = y0 - self.L1*cos(self.th1)

        return (x0, x1, y0, y1, self.t, self.L0, self.L1, self.th0, self.th1)

    def advance(self):
        return self.simulate()

