Napoleon
########

Dicebat Bernardus Carnotensis nos esse quasi nanos, gigantium humeris insidentes, ut possimus  plura  eis  et  remotiora  videre,  non  utique  proprii  visus  acumine,  aut  eminentia  corporis, sed quia in altum subvenimur et extollimur magnitudine gigantea

Bernard of Chartres used to compare us to dwarfs perched on the shoulders of giants. He pointed out that we see more and farther than our predecessors, not because we have keener vision or greater height, but because we are lifted up and borne aloft on their gigantic stature.

Napoleon help you build better python application

Supports Python **3.10**.


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
