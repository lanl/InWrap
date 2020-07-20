#ifndef _VTK_MPI_H_
#define _VTK_MPI_H_

#include <string>
#include <iostream>

#include <mpi.h>

#include <vtkMPIController.h>


namespace InWrap
{

class VTKMpi
{
	vtkMPIController* controller;

  public:
	VTKMpi();
	VTKMpi(int external);
	~VTKMpi();

	void init();
	void terminate();
};



inline VTKMpi::VTKMpi()
{
  	controller = NULL;
}

inline VTKMpi::VTKMpi(int external)
{
	controller = NULL;
  	init();
}

inline VTKMpi::~VTKMpi()
{
	terminate();
}



inline void VTKMpi::init()
{
	controller = vtkMPIController::New();
  	controller->Initialize(NULL, NULL, 1);
  	controller->SetGlobalController(controller);
}

inline void VTKMpi::terminate()
{
	if (controller != NULL)
	{
		controller->Finalize(1);
		controller->Delete();
		controller = NULL;
	}
}

} //inwrap

#endif