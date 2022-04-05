Napoleon
########

Dicebat Bernardus Carnotensis nos esse quasi nanos, gigantium humeris insidentes, ut possimus  plura  eis  et  remotiora  videre,  non  utique  proprii  visus  acumine,  aut  eminentia  corporis, sed quia in altum subvenimur et extollimur magnitudine gigantea

Napoleon help you build better python application

Supports Python **3.10**.


..code-block:: python

   >>> from napoleon import AbstractObject, Integer, retry, String
   >>> 
   >>> class Vehicle(AbstractObject):
   ...     number_of_wheels = Integer(minimum=2, multiple_of=2, default=4)
   ...     sound_at_failing_start = String(default="brr")
   ...     @retry()
   ...     def try_to_start(self):
   ...         print(self.sound_at_failing_start)
   ...         raise RuntimeError("Could not start the vehicle")
   ... 
   >>> car = Vehicle()
   >>> car.try_to_start()
   brr
   brr
   brr
   RuntimeError: Could not start the vehicle
   >>> moto = Vehicle(number_of_wheels=2, sound_at_failing_start="Vroum...")
   >>> moto.try_to_start.max_retry = 5
   >>> moto.serialize()
   {'number_of_wheels': 2, 'sound_at_failing_start': 'Vroum...', 'try_to_start': {'max_retry': 5, 'delay': 3.0, 'class_name': 'Retrier'}, 'class_name': 'Vehicle'}
   >>> moto.try_to_start()
   Vroum...
   Vroum...
   Vroum...
   Vroum...
   Vroum...
   RuntimeError: Could not start the vehicle
