"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class netnamespaces_intro(ShutItModule):


	def build(self, shutit):
		# https://www.youtube.com/watch?v=_WgUwUf1d34
		shutit.send('rm -rf /tmp/netnamespaces_intro_vm')
		shutit.send('mkdir -p /tmp/netnamespaces_intro_vm')
		shutit.send('cd /tmp/netnamespaces_intro_vm')
		shutit.send('vagrant init ubuntu/trusty64')
		shutit.send('vagrant up --provider virtualbox')
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -')
		shutit.install('openvswitch-switch')
		shutit.install('dnsmasq')
		shutit.send('ip link',note='Show the network interfaces on the VM')
		shutit.send('ip addr',note='Show the ip address')
		shutit.send('ip route',note='Show the routing table')
		shutit.send('ip netns add red',note='Add the red ip net namespace')
		shutit.send('ip netns add green',note='Add the green ip net namespace')
		shutit.send('ip netns',note='List the network namespaces')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns add amistake',note='Add the amistake namespace ready to delete')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns del amistake',note='Delete the mistakenly added network namespace')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns exec red ip link',note='Run the ip link command from within the red network namespace. Note it is down.')
		# We now use OpenVSwitch to act as a switch for these two network namespaces.
		shutit.send('ovs-vsctl add-br OVS-1',note='Create a network bridge on the host called OVS-1 using openvswitch')
		shutit.send('ovs-vsctl show',note='OVS-1 interface has been added by OpenVSwitch')
		shutit.send('ip link',note='OVS-1 interface has been added')
		# Now to connect these together Root namespace: OVS-1 (->Red, ->Green) - OVS-1 using veth pairs
		# They act like a pipe. 
		shutit.send('ip link add eth0-r type veth peer name veth-r',note='ip link add adds one end (eth0-r) in the red namespace which peers with the other end (veth-r) connected to OVS-1. They are not connected to anything yet')
		shutit.send('ip link',note='The pipe is not connected to anything yet and both ends can be seen in the root namespace')
		shutit.send('ip link set eth0-r netns red',note='Sets the eth0-r link into the red net namespace')
		shutit.send('ip link',note='We cannot see the eth0-r link anymore in the root namespace')
		shutit.send('ip netns exec red ip link',note='It is now in the red net namespace')
		shutit.send('ovs-vsctl add-port OVS-1 veth-r',note='Attach the other end of the veth pair to the virtual switch')
		shutit.send('ovs-vsctl show',note='The veth-r port is now attached to the virtual switch')

		shutit.send('ip link add eth0-g type veth peer name veth-g',note='ip link add adds one end (eth0-g) in the red namespace which peers with the other end (veth-g) connected to OVS-1. They are not connected to anything yet')
		shutit.send('ip link set eth0-g netns green',note='Sets the eth0-g link into the green net namespace')
		shutit.send('ip netns exec green ip link',note='It is now in the green net namespace')
		shutit.send('ovs-vsctl add-port OVS-1 veth-g',note='Attach the other end of the veth pair to the virtual switch')
		# Turn interfaces up and assign IP addresses (10mins into video)
		shutit.send('ip link',note='red namespace linked to OVS-1 in veth-r is DOWN')
		shutit.send('ip link set veth-r up',note='Turn up the veth-r interface')
		shutit.send('ip link',note='red namespace linked to OVS-1 in veth-r is UP')
		shutit.send('ip netns exec red ip link set dev lo up',note='turn up loopback dev in red namespace')
		shutit.send('ip netns exec red ip link set dev eth0-r up',note='turn up dev in red namespace, ie the other end of the veth pipe')
		shutit.send('ip netns exec red ip address add 10.0.0.1/24 dev eth0-r',note='assign an ip address to the end of the veth pair')
		shutit.send('ip netns exec red ip a',note='Interfaces UP and ip address assigned to eth0-r')
		shutit.send('ip netns exec red ip route',note='Network is set up for the namespace')
		shutit.send('ip route',note='Root namespace has no awareness of 10.0.0.0/24. It is isolated')

		shutit.send('ip link set veth-g up',note='Turn up the veth-g interface')
		shutit.send('ip netns exec green ip link set dev lo up',note='turn up loopback dev in green namespace')
		shutit.send('ip netns exec green ip link set dev eth0-g up',note='turn up dev in green namespace, ie the other end of the veth pipe')
		shutit.send('ip netns exec green ip address add 10.0.0.2/24 dev eth0-g',note='assign an ip address to the end of the veth pair')

		shutit.login(command='ip netns exec red bash',note='Enter red network namespace')
		shutit.send('ping -c 3 10.0.0.2',note='We should be able to ping the other network')
		shutit.logout()
	
		# Create vlans
		shutit.send('ovs-vsctl set port veth-r tag=100',note='Move the red veth to VLAN 100')
		shutit.send('ovs-vsctl set port veth-g tag=200',note='Move the green veth to VLAN 200')
		shutit.send('ip netns exec red ip address del 10.0.0.1/24 dev eth0-r',note='Since the namespaces are on separate VLANs, we now want to scrub the IP addresses. Do the red one.')
		shutit.send('ip netns exec green ip address del 10.0.0.2/24 dev eth0-g',note='Since the namespaces are on separate VLANs, we now want to scrub the IP addresses. Do the green one.')
		
		# Add two new net namespaces for our DHCP servers.
		# Connect through OpenVSwitch internal ports this time rather than veth pairs.
		shutit.send('ip netns add dhcp-r',note='We are going to hook up two new namespaces directly to the OpenVSwitch using internal ports rather than through a veth pair. Add a net namespace for our red dhcp server.')
		shutit.send('ip netns add dhcp-g',note='Add a net namespace for the green dhcp server')

		shutit.send('ovs-vsctl add-port OVS-1 tap-r',note='Creates a new port on openvswitch for the red dhcp namespace')
		shutit.send('ovs-vsctl set interface tap-r type=internal',note='Set the port to the internal type')
		shutit.send('ovs-vsctl set port tap-r tag=100',note='Places the port into VLAN100')

		shutit.send('ovs-vsctl add-port OVS-1 tap-g',note='Creates a new port on openvswitch for the green dhcp namespace')
		shutit.send('ovs-vsctl set interface tap-g type=internal',note='Set the port to the internal type')
		shutit.send('ovs-vsctl set port tap-g tag=200',note='Places the port into VLAN200')

		shutit.send('ovs-vsctl show',note='Check the configuration. You will see the two new ports')

		shutit.send('ip link',note='The new ports are still in the root namespace. We are going to move them to their dhcp namespace')
		shutit.send('ip link set tap-r netns dhcp-r',note='Put the tap-r port into the dhcp-r namespace from the root namespace')
		shutit.send('ip link set tap-g netns dhcp-g',note='Put the tap-g port into the dhcp-g namespace from the root namespace')
		shutit.send('ip link',note='The ports are gone from root namespace')

		shutit.login(command='ip netns exec dhcp-r bash',note='Enter the new red dhcp namespace')
		shutit.send('ip link set dev lo up',note='Turn up loopback interface')
		shutit.send('ip link set dev tap-r up',note='Turn up tap-r interface')
		shutit.send('ip address add 10.50.50.2/24 dev tap-r',note='Give the new interface a name')
		shutit.logout(note='Exit the net namespace')

		shutit.login(command='ip netns exec dhcp-g bash',note='Enter the new green dhcp namespace')
		shutit.send('ip link set dev lo up',note='Turn up loopback interface')
		shutit.send('ip link set dev tap-g up',note='Turn up tap-g interface')
		shutit.send('ip address add 10.50.50.2/24 dev tap-g',note='Give the new interface a name, we can use the same address as before as we are on different VLANs')
		shutit.logout(note='Exit the net namespace')

		# Now run dnsmasq processes
		shutit.send('ip netns exec dhcp-r dnsmasq --interface=tap-r --dhcp-range 10.50.50.10,10.50.50.100,255.255.255.0',note='Set up the dnsmasq process in the red namespace')
		shutit.send('ip netns exec dhcp-g dnsmasq --interface=tap-g --dhcp-range 10.50.50.10,10.50.50.100,255.255.255.0',note='Set up the dnsmasq process in the green namespace')

		shutit.send('''ip netns identify $(ps -ef | grep 'nobody.*dnsmasq' | grep -v grep | awk '{print $2}' | head -1)''',note='Show that the dnsmasq pid belongs to a namespace we just created')
		shutit.send('''ip netns identify $(ps -ef | grep 'nobody.*dnsmasq' | grep -v grep | awk '{print $2}' | tail -1)''',note='Show that the dnsmasq pid belongs to a namespace we just created')

		shutit.send('ip netns exec red dhclient eth0-r',note='Get an ip address from dhcp on the eth0-r interface in the red namespace')
		shutit.send('ip netns exec red ip a',note='Show the ip address in the red namespace')
		shutit.send('ip netns exec green dhclient eth0-g',note='Get an ip address from dhcp on the eth0-g interface in the green namespace')
		shutit.send('ip netns exec green ip a',note='Show the ip address in the green namespace')

		shutit.logout()
		shutit.logout()
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is 
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return netnamespaces_intro(
		'shutit.netnamespaces_intro.netnamespaces_intro.netnamespaces_intro', 1259389554.00,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['tk.shutit.vagrant.vagrant.vagrant','shutit-library.virtualbox.virtualbox.virtualbox']
	)

