
from _pen2 import *
from math import pi

DEFAULT_M0 = 1.0
DEFAULT_M1 = 1.2
DEFAULT_L0 = 1.00
DEFAULT_L1 = 0.75
DEFAULT_ITH0 = 0.001*int(1000*pi)
DEFAULT_ITH1 = DEFAULT_ITH0 - 0.001
DEFAULT_IW0 = 0.0
DEFAULT_IW1 = 0.0
# NOTE(opadron): Simulation seems to go in slow motion with the standard gravity
# constant, so just use a default at 10X strength.
DEFAULT_G = 98.1
DEFAULT_DT = 0.001*int(1000.0/60.0)
DEFAULT_DURATION = None

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="run a double pendulum simulation")
    parser.add_argument(
        "--mass0", "-m0", type=float, default=DEFAULT_M0, metavar="M0",
        help="Mass of the first pendulum weight (kg).")
    parser.add_argument(
        "--mass1", "-m1", type=float, default=DEFAULT_M1, metavar="M1",
        help="Mass of the second pendulum weight (kg).")
    parser.add_argument(
        "--length0", "-L0", type=float, default=DEFAULT_L0, metavar="L0",
        help="Length of the first pendulum arm (m).")
    parser.add_argument(
        "--length1", "-L1", type=float, default=DEFAULT_L1, metavar="L1",
        help="Length of the second pendulum arm (m).")
    parser.add_argument(
        "--theta0", "-th0", type=float, default=DEFAULT_ITH0, metavar="TH0",
        help=("Initial angle of the first pendulum arm (radians).  "
              "Zero (0.0) is pointing straight down."))
    parser.add_argument(
        "--theta1", "-th1", type=float, default=DEFAULT_ITH1, metavar="TH0",
        help=("Initial angle of the second pendulum arm (radians).  "
              "Zero (0.0) is pointing parallel to the first arm."))
    parser.add_argument(
        "--omega0", "-w0", type=float, default=DEFAULT_IW0, metavar="W0",
        help="Initial anglular velocity of the first pendulum arm (radians/s).")
    parser.add_argument(
        "--omega1", "-w1", type=float, default=DEFAULT_IW1, metavar="W1",
        help=("Initial anglular velocity of the "
              "second pendulum arm (radians/s)."))
    parser.add_argument(
        "--gravity", "-g", type=float, default=DEFAULT_G, metavar="G",
        help=("Strength of the constant downward acceleration "
              "felt by both pendulum weights due to gravity (m/s^2)."))
    parser.add_argument(
        "--time_step", "-dt", type=float, default=DEFAULT_DT, metavar="DT",
        help="Simulation time step size (s).")
    parser.add_argument(
        "--duration", "-d", type=float, default=DEFAULT_DURATION, metavar="D",
        help="Simulation duration (s).")

    args = parser.parse_args()
    run_simulation(mass0=args.mass0,
                   mass1=args.mass1,
                   length0=args.length0,
                   length1=args.length1,
                   theta0=args.theta0,
                   theta1=args.theta1,
                   omega0=args.omega0,
                   omega1=args.omega1,
                   gravity=args.gravity,
                   time_step=args.time_step,
                   duration=args.duration)

def run_simulation(**kwds):
    from math import pi, sqrt, sin, cos
    from vtk import vtkInteractorStyleTerrain, \
                    vtkRenderWindowInteractor, \
                    vtkRenderWindow, \
                    vtkRenderer, \
                    vtkActor, \
                    vtkPolyDataMapper, \
                    vtkSphereSource, \
                    vtkCylinderSource, \
                    vtkTransform

    from vtk.util.colors import red, blue, brown

    M0 = kwds.get("mass0", DEFAULT_M0)
    M1 = kwds.get("mass1", DEFAULT_M1)
    L0 = kwds.get("length0", DEFAULT_L0)
    L1 = kwds.get("length1", DEFAULT_L1)
    iTH0 = kwds.get("theta0", DEFAULT_ITH0)
    iTH1 = kwds.get("theta1", DEFAULT_ITH1)
    iW0 = kwds.get("omega0", DEFAULT_IW0)
    iW1 = kwds.get("omega1", DEFAULT_IW1)
    G = kwds.get("gravity", DEFAULT_G)
    dt = kwds.get("time_step", DEFAULT_DT)
    duration = kwds.get("duration", DEFAULT_DURATION)

    sim = Pen2Sim(iTH0, iTH1, iW0, iW1, M0, M1, L0, L1, G, dt)

    sphere0 = vtkSphereSource()
    sphere1 = vtkSphereSource()

    cylinder0 = vtkCylinderSource()
    cylinder1 = vtkCylinderSource()

    sphere0.SetCenter(0.0, 0.0, 0.0)
    sphere1.SetCenter(0.0, 0.0, 0.0)

    sphere0.SetRadius(0.25*sqrt(M0/pi))
    sphere1.SetRadius(0.25*sqrt(M1/pi))

    cylinder0.SetRadius(0.04)
    cylinder1.SetRadius(0.04)

    cTran0 = vtkTransform()
    cTran1 = vtkTransform()

    sMap0 = vtkPolyDataMapper()
    sMap1 = vtkPolyDataMapper()

    cMap0 = vtkPolyDataMapper()
    cMap1 = vtkPolyDataMapper()

    sMap0.SetInputConnection(sphere0.GetOutputPort())
    sMap1.SetInputConnection(sphere1.GetOutputPort())

    cMap0.SetInputConnection(cylinder0.GetOutputPort())
    cMap1.SetInputConnection(cylinder1.GetOutputPort())

    sAct0 = vtkActor()
    sAct1 = vtkActor()
    sAct0.SetMapper(sMap0)
    sAct1.SetMapper(sMap1)
    sAct0.GetProperty().SetColor(red)
    sAct1.GetProperty().SetColor(blue)

    cAct0 = vtkActor()
    cAct1 = vtkActor()
    cAct0.SetMapper(cMap0)
    cAct1.SetMapper(cMap1)
    cAct0.GetProperty().SetColor(brown)
    cAct1.GetProperty().SetColor(brown)

    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtkInteractorStyleTerrain())
    interactor.SetRenderWindow(renderWindow)

    renderer.AddActor(sAct0)
    renderer.AddActor(sAct1)
    renderer.AddActor(cAct0)
    renderer.AddActor(cAct1)
    renderer.SetBackground(0.1, 0.2, 0.4)
    renderer.GetActiveCamera().Dolly(0.125)

    renderWindow.SetSize(800, 600)

    renderWindow.Render()
    interactor.Initialize()

    state = [None]
    def callback(*args, **kwds):
        if state[0] is None:
            state[0] = list(sim.initial_state())
            cylinder0.SetHeight(state[0][5])
            cylinder1.SetHeight(state[0][6])

        else:
            state[0][:] = sim.advance()

        x0, x1, y0, y1, t, L0, L1, th0, th1 = state[0][:9]

        cTran0.Identity()
        cTran1.Identity()

        cTran1.Translate(x0, y0, 0.0)

        cTran0.RotateZ(180.0*(th0      )/pi)
        cTran1.RotateZ(180.0*(      th1)/pi)

        cTran0.Translate(0.0, -0.5*L0, 0.0)
        cTran1.Translate(0.0, -0.5*L1, 0.0)

        cAct0.SetUserTransform(cTran0)
        cAct1.SetUserTransform(cTran1)

        sAct0.SetPosition(x0, y0, 0.0)
        sAct1.SetPosition(x1, y1, 0.0)
        renderWindow.Render()

        if duration is not None and t >= duration:
            interactor.RemoveObserver(timerid)
            interactor.ExitCallback()

    interactor.AddObserver("TimerEvent", callback)
    timerid = interactor.CreateRepeatingTimer(int(1000*dt));

    interactor.Start()

