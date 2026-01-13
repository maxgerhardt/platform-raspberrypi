#include "mbed.h"

int main()
{
	while(true) 
	{
		printf("Hello world from Mbed CE!\n");
		ThisThread::sleep_for(1s);
	}

	// main() is expected to loop forever.
	// If main() actually returns the processor will halt
	return 0;
}