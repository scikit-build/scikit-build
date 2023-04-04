subroutine bonjour
  print *, "Bonjour le monde!"
end subroutine bonjour

integer function change_integer(n)
    implicit none

    integer, intent(in) :: n
    integer, parameter :: power = 2

    change_integer = n ** power
end function change_integer
